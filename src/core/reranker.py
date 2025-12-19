"""
Re-ranker Service
Cross-encoder re-ranking for better retrieval quality
"""

from typing import List, Dict, Optional, Any
import numpy as np
from ..shared import get_logger

logger = get_logger(__name__)

# Try to import CrossEncoder, but make it optional
try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    logger.warning("sentence-transformers not available. Re-ranking will be disabled.")


class Reranker:
    """
    Re-ranker using cross-encoder for better ranking quality
    Cross-encoders are more accurate than bi-encoders but slower
    Best practice: Use bi-encoder for retrieval (fast), cross-encoder for re-ranking (accurate)
    """
    
    def __init__(
        self,
        model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2',
        max_length: int = 512,
        enable_reranking: bool = True
    ):
        """
        Initialize re-ranker
        
        Args:
            model_name: Cross-encoder model name
            max_length: Maximum sequence length
            enable_reranking: Enable re-ranking (can be disabled if model not available)
        """
        self.model_name = model_name
        self.max_length = max_length
        self.enable_reranking = enable_reranking and CROSS_ENCODER_AVAILABLE
        
        if self.enable_reranking:
            try:
                logger.info(f"Loading cross-encoder model: {model_name}")
                self.model = CrossEncoder(model_name, max_length=max_length)
                logger.info(f"✅ Reranker initialized with {model_name}")
            except Exception as e:
                logger.error(f"Failed to load cross-encoder model: {e}")
                self.enable_reranking = False
                self.model = None
        else:
            self.model = None
            if not CROSS_ENCODER_AVAILABLE:
                logger.warning("Cross-encoder not available. Install with: pip install sentence-transformers")
            else:
                logger.info("Re-ranking disabled")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on query relevance
        
        Args:
            query: Query text
            documents: List of documents to re-rank
            top_k: Return only top K results (None = return all)
            
        Returns:
            Re-ranked list of documents with rerank_score
        """
        if not self.enable_reranking or not documents:
            # Return documents as-is with original scores
            for doc in documents:
                if 'rerank_score' not in doc:
                    doc['rerank_score'] = doc.get('score', 0.0)
            return documents[:top_k] if top_k else documents
        
        try:
            # Extract texts from documents
            texts = []
            for doc in documents:
                payload = doc.get('payload', {})
                # Try multiple text fields
                text = (
                    payload.get('page_content') or
                    payload.get('semantic_text') or
                    payload.get('text') or
                    payload.get('content') or
                    payload.get('description') or
                    ''
                )
                texts.append(text)
            
            # Create query-document pairs
            pairs = [(query, text) for text in texts]
            
            # Get relevance scores from cross-encoder
            logger.debug(f"Re-ranking {len(pairs)} documents with cross-encoder")
            scores = self.model.predict(pairs, show_progress_bar=False)
            
            # Convert to list if numpy array
            if isinstance(scores, np.ndarray):
                scores = scores.tolist()
            
            # Combine documents with scores
            reranked_docs = []
            for doc, score in zip(documents, scores):
                doc_copy = doc.copy()
                doc_copy['rerank_score'] = float(score)
                # Keep original score for reference
                doc_copy['original_score'] = doc.get('score', 0.0)
                reranked_docs.append(doc_copy)
            
            # Sort by rerank_score (descending)
            reranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Return top_k if specified
            if top_k:
                reranked_docs = reranked_docs[:top_k]
            
            logger.info(f"✅ Re-ranked {len(reranked_docs)} documents")
            return reranked_docs
            
        except Exception as e:
            logger.error(f"Error during re-ranking: {e}")
            # Fallback: return documents sorted by original score
            sorted_docs = sorted(
                documents,
                key=lambda x: x.get('score', 0.0),
                reverse=True
            )
            return sorted_docs[:top_k] if top_k else sorted_docs
    
    def rerank_batch(
        self,
        queries: List[str],
        documents_list: List[List[Dict[str, Any]]],
        top_k: Optional[int] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Re-rank multiple query-document sets in batch
        
        Args:
            queries: List of queries
            documents_list: List of document lists (one per query)
            top_k: Return only top K results per query
            
        Returns:
            List of re-ranked document lists
        """
        results = []
        for query, documents in zip(queries, documents_list):
            reranked = self.rerank(query, documents, top_k=top_k)
            results.append(reranked)
        return results
    
    def is_available(self) -> bool:
        """Check if re-ranking is available"""
        return self.enable_reranking and self.model is not None


class DiversityReranker:
    """
    Diversity re-ranker to ensure diverse recommendations
    Prevents repetitive results by penalizing similar items
    """
    
    def __init__(self, diversity_weight: float = 0.3):
        """
        Initialize diversity re-ranker
        
        Args:
            diversity_weight: Weight for diversity (0.0 = no diversity, 1.0 = only diversity)
        """
        self.diversity_weight = diversity_weight
        logger.info(f"✅ DiversityReranker initialized (weight={diversity_weight})")
    
    def rerank(
        self,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        feature_extractor: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents considering diversity
        
        Args:
            documents: List of documents to re-rank
            top_k: Return only top K results
            feature_extractor: Function to extract features from document (optional)
            
        Returns:
            Re-ranked list of documents with diversity_score
        """
        if not documents:
            return []
        
        # Default feature extractor
        if feature_extractor is None:
            feature_extractor = self._default_feature_extractor
        
        reranked = []
        used_features = set()
        
        # Sort by original score first
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get('score', x.get('rerank_score', 0.0)),
            reverse=True
        )
        
        for doc in sorted_docs:
            # Extract features
            features = feature_extractor(doc)
            feature_key = self._features_to_key(features)
            
            # Calculate diversity score
            diversity_score = self._calculate_diversity(feature_key, used_features)
            
            # Get relevance score
            relevance_score = doc.get('rerank_score', doc.get('score', 0.0))
            
            # Combine relevance and diversity
            final_score = (1 - self.diversity_weight) * relevance_score + \
                         self.diversity_weight * diversity_score
            
            doc_copy = doc.copy()
            doc_copy['diversity_score'] = diversity_score
            doc_copy['final_score'] = final_score
            reranked.append(doc_copy)
            
            # Add to used features
            used_features.add(feature_key)
        
        # Sort by final score
        reranked.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Return top_k if specified
        if top_k:
            reranked = reranked[:top_k]
        
        logger.debug(f"Diversity re-ranked {len(reranked)} documents")
        return reranked
    
    def _default_feature_extractor(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Default feature extractor for hotel documents"""
        payload = doc.get('payload', {})
        return {
            'area_id': payload.get('area_id'),
            'hotel_rank': payload.get('hotel_rank'),
            'price_range': self._get_price_range(payload.get('hotel_price_average', 0)),
            'document_type': payload.get('document_type')
        }
    
    def _get_price_range(self, price: float) -> str:
        """Categorize price into range"""
        if price < 1000000:
            return 'budget'
        elif price < 3000000:
            return 'mid'
        elif price < 5000000:
            return 'premium'
        else:
            return 'luxury'
    
    def _features_to_key(self, features: Dict[str, Any]) -> str:
        """Convert features to string key"""
        return str(sorted(features.items()))
    
    def _calculate_diversity(self, feature_key: str, used_features: set) -> float:
        """Calculate diversity score (1.0 = completely new, 0.0 = duplicate)"""
        if not used_features:
            return 1.0
        
        if feature_key in used_features:
            return 0.0
        
        # Partial match: check if any feature values overlap
        # Simple implementation: return 1.0 if key not in used_features
        # More sophisticated: calculate overlap percentage
        return 1.0


class HybridReranker:
    """
    Hybrid re-ranker combining cross-encoder and diversity
    """
    
    def __init__(
        self,
        cross_encoder_model: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2',
        diversity_weight: float = 0.2,
        enable_cross_encoder: bool = True
    ):
        """
        Initialize hybrid re-ranker
        
        Args:
            cross_encoder_model: Cross-encoder model name
            diversity_weight: Weight for diversity (0.0-1.0)
            enable_cross_encoder: Enable cross-encoder re-ranking
        """
        self.cross_encoder_reranker = Reranker(
            model_name=cross_encoder_model,
            enable_reranking=enable_cross_encoder
        ) if enable_cross_encoder else None
        
        self.diversity_reranker = DiversityReranker(diversity_weight=diversity_weight)
        
        logger.info(f"✅ HybridReranker initialized (cross_encoder={enable_cross_encoder}, diversity_weight={diversity_weight})")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        use_diversity: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents using cross-encoder and optionally diversity
        
        Args:
            query: Query text
            documents: List of documents to re-rank
            top_k: Return only top K results
            use_diversity: Apply diversity re-ranking after cross-encoder
            
        Returns:
            Re-ranked list of documents
        """
        # Step 1: Cross-encoder re-ranking
        if self.cross_encoder_reranker and self.cross_encoder_reranker.is_available():
            reranked = self.cross_encoder_reranker.rerank(query, documents, top_k=None)
        else:
            reranked = documents
        
        # Step 2: Diversity re-ranking (optional)
        if use_diversity and len(reranked) > 1:
            reranked = self.diversity_reranker.rerank(reranked, top_k=top_k)
        elif top_k:
            reranked = reranked[:top_k]
        
        return reranked
