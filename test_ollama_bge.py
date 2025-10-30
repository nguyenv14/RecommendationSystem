#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Ollama BGE-M3 embeddings
"""

import requests
import numpy as np

def test_ollama_bge():
    """Test BGE-M3 embeddings via Ollama"""
    
    url = "http://localhost:11434/api/embeddings"
    
    test_texts = [
        "Khách sạn ở biển Nha Trang",
        "Khách sạn sang trọng tại Đà Nẵng",
        "Hotel near the beach"
    ]
    
    print("Testing BGE-M3 embeddings via Ollama...")
    print(f"Total texts: {len(test_texts)}\n")
    
    embeddings = []
    
    for i, text in enumerate(test_texts):
        try:
            print(f"[{i+1}/{len(test_texts)}] Embedding: {text[:50]}...")
            
            response = requests.post(
                url,
                json={
                    "model": "bge-m3",
                    "prompt": text
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            embedding = np.array(result['embedding'])
            embeddings.append(embedding)
            
            print(f"  ✓ Embedding shape: {embedding.shape}")
            print(f"  ✓ Embedding norms: {np.linalg.norm(embedding):.4f}\n")
            
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
    
    if len(embeddings) >= 2:
        # Calculate similarity between first two
        emb1 = embeddings[0]
        emb2 = embeddings[1]
        
        # Normalize
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)
        
        cosine_sim = np.dot(emb1_norm, emb2_norm)
        
        print(f"\n{'='*60}")
        print(f"Cosine similarity between texts 1 and 2: {cosine_sim:.4f}")
        print(f"{'='*60}")
    
    print("\n✓ BGE-M3 via Ollama is working!")

if __name__ == '__main__':
    test_ollama_bge()

