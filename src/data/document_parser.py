#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Parser Module
Parse various document formats (PDF, DOCX, DOC, TXT) and extract text content
"""

import os
import tempfile
import requests
import hashlib
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for various document formats"""
    
    def __init__(self):
        """Initialize document parser"""
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt']
    
    def parse_from_url(self, file_url: str, file_name: Optional[str] = None) -> Tuple[str, str]:
        """
        Download and parse document from URL
        
        Args:
            file_url: URL of the document
            file_name: Optional file name (if not provided, will extract from URL)
            
        Returns:
            Tuple of (text_content, file_name)
            
        Raises:
            ValueError: If file format is not supported or parsing fails
            requests.RequestException: If download fails
        """
        logger.info(f"Downloading file from: {file_url}")
        
        # Download file
        response = requests.get(file_url, timeout=30)
        if response.status_code != 200:
            raise requests.RequestException(
                f'Failed to download file: HTTP {response.status_code}'
            )
        
        # Determine file name and extension
        if not file_name:
            # Try to extract from URL
            file_name = os.path.basename(file_url.split('?')[0]) or 'document'
        
        # Extract extension from file_name first
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # If no extension in file_name, try to extract from URL
        if not file_ext:
            url_path = file_url.split('?')[0]  # Remove query parameters
            url_ext = os.path.splitext(url_path)[1].lower()
            if url_ext in self.supported_formats:
                file_ext = url_ext
                # Add extension to file_name if it doesn't have one
                if not file_name.endswith(file_ext):
                    file_name = file_name + file_ext
        
        # If still no extension, try to detect from Content-Type header
        if not file_ext:
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' in content_type:
                file_ext = '.pdf'
                file_name = file_name + '.pdf' if not file_name.endswith('.pdf') else file_name
            elif 'msword' in content_type or 'wordprocessingml' in content_type:
                file_ext = '.docx'
                file_name = file_name + '.docx' if not file_name.endswith('.docx') else file_name
            elif 'plain' in content_type:
                file_ext = '.txt'
                file_name = file_name + '.txt' if not file_name.endswith('.txt') else file_name
        
        if not file_ext or file_ext not in self.supported_formats:
            raise ValueError(f'Unsupported file format: "{file_ext}" (file: {file_name}). Supported: {self.supported_formats}')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            # Parse file
            text_content = self.parse_file(tmp_path, file_ext)
            return text_content, file_name
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {tmp_path}: {e}")
    
    def parse_file(self, file_path: str, file_ext: Optional[str] = None) -> str:
        """
        Parse file and extract text content
        
        Args:
            file_path: Path to the file
            file_ext: Optional file extension (if not provided, will extract from path)
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported or parsing fails
        """
        if not file_ext:
            file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f'Unsupported file format: {file_ext}. Supported: {self.supported_formats}')
        
        logger.info(f"Parsing {file_ext} file: {file_path}")
        
        text_content = ""
        
        if file_ext == '.pdf':
            text_content = self._parse_pdf(file_path)
        elif file_ext in ['.doc', '.docx']:
            text_content = self._parse_docx(file_path)
        elif file_ext == '.txt':
            text_content = self._parse_txt(file_path)
        else:
            # Try to read as plain text as fallback
            text_content = self._parse_txt(file_path)
        
        if not text_content or not text_content.strip():
            raise ValueError('No text content extracted from file')
        
        logger.info(f"Extracted {len(text_content)} characters from file")
        return text_content
    
    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file"""
        text_content = ""
        
        # Try PyPDF2 first
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            return text_content
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"PyPDF2 parsing failed: {e}, trying pdfplumber...")
        
        # Try pdfplumber as fallback
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            return text_content
        except ImportError:
            raise ImportError(
                'PDF parsing requires PyPDF2 or pdfplumber. '
                'Please install: pip install PyPDF2 pdfplumber'
            )
        except Exception as e:
            raise ValueError(f'Failed to parse PDF: {str(e)}')
    
    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX/DOC file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            return text_content
        except ImportError:
            raise ImportError(
                'DOCX parsing requires python-docx. '
                'Please install: pip install python-docx'
            )
        except Exception as e:
            raise ValueError(f'Failed to parse DOCX: {str(e)}')
    
    def _parse_txt(self, file_path: str) -> str:
        """Parse plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f'Failed to parse text file: {str(e)}')


class DocumentIndexer:
    """Service to index parsed documents into Qdrant"""
    
    def __init__(self, collection_name: str = 'policy_documents'):
        """
        Initialize document indexer
        
        Args:
            collection_name: Name of the Qdrant collection
        """
        from src.core.rag import RAGService
        from src.data.chunker import SmartChunker
        
        self.rag_service = RAGService(collection_name=collection_name)
        self.collection_name = collection_name
        self.chunker = None  # Will be initialized when needed
    
    def index_document(
        self,
        text_content: str,
        file_name: str,
        file_url: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 200
    ) -> Dict[str, Any]:
        """
        Chunk and index document into Qdrant
        
        Args:
            text_content: Extracted text content from document
            file_name: Name of the file
            file_url: URL of the file
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            min_chunk_size: Minimum size of chunk
            
        Returns:
            Dictionary with indexing results
        """
        # Initialize chunker if not already done
        if self.chunker is None:
            from src.data.chunker import SmartChunker
            self.chunker = SmartChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                min_chunk_size=min_chunk_size,
                preserve_sentences=True
            )
        
        # Chunk the text
        chunks = self.chunker.split_text(text_content)
        logger.info(f"Created {len(chunks)} chunks from file {file_name}")
        
        # Prepare documents for indexing
        documents = []
        # Create a unique base ID from file name hash
        file_hash = int(hashlib.md5(file_name.encode()).hexdigest()[:8], 16)
        base_id = 4000000 + (file_hash % 1000000)  # Offset to avoid collision with hotels/rooms
        
        for idx, chunk in enumerate(chunks):
            # Create unique integer ID for Qdrant
            doc_id = base_id + idx
            doc = {
                'id': doc_id,
                'text': chunk,
                'file_name': file_name,
                'file_url': file_url,
                'chunk_index': idx,
                'total_chunks': len(chunks),
                'document_type': 'policy',
                'collection_name': self.collection_name
            }
            documents.append(doc)
        
        # Index documents
        success = self.rag_service.index_documents(
            documents=documents,
            id_field='id',
            text_field='text',
            metadata_fields=['file_name', 'file_url', 'chunk_index', 'total_chunks', 'document_type', 'collection_name'],
            recreate_collection=False
        )
        
        if not success:
            raise RuntimeError('Failed to index documents into Qdrant')
        
        return {
            'file_name': file_name,
            'chunks_count': len(chunks),
            'collection_name': self.collection_name,
            'text_length': len(text_content),
            'success': True
        }


class DocumentService:
    """High-level service combining parsing and indexing"""
    
    def __init__(self, collection_name: str = 'policy_documents'):
        """
        Initialize document service
        
        Args:
            collection_name: Name of the Qdrant collection
        """
        self.parser = DocumentParser()
        self.indexer = DocumentIndexer(collection_name=collection_name)
    
    def parse_and_index(
        self,
        file_url: str,
        file_name: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Parse document from URL and index into Qdrant
        
        Args:
            file_url: URL of the document
            file_name: Optional file name
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dictionary with parsing and indexing results
        """
        # Parse document
        text_content, actual_file_name = self.parser.parse_from_url(file_url, file_name)
        
        # Index document
        result = self.indexer.index_document(
            text_content=text_content,
            file_name=actual_file_name,
            file_url=file_url,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return result

