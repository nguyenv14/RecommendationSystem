#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Collections Script
Check and verify Qdrant collections configuration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
import logging
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def verify_collections(qdrant_url: str = "http://localhost:6333"):
    """
    Verify collections and show detailed information
    
    Args:
        qdrant_url: Qdrant server URL
    """
    logger.info("="*80)
    logger.info("📊 Qdrant Collections Verification")
    logger.info("="*80)
    logger.info(f"Qdrant URL: {qdrant_url}\n")
    
    try:
        client = QdrantClient(url=qdrant_url)
        
        # Get all collections
        collections = client.get_collections()
        
        if not collections.collections:
            logger.info("⚠️  No collections found")
            return
        
        logger.info(f"Found {len(collections.collections)} collection(s)\n")
        
        # Collect data for table
        table_data = []
        
        for col in collections.collections:
            try:
                info = client.get_collection(col.name)
                
                # Determine system
                if "rag" in col.name:
                    system = "🤖 RAG"
                elif "recommendation" in col.name:
                    system = "🎯 Recommendation"
                else:
                    system = "❓ Unknown"
                
                # Get vector config
                vector_size = info.config.params.vectors.size
                distance = str(info.config.params.vectors.distance).split('.')[-1]
                
                # Get points count
                points_count = info.points_count
                
                # Status
                if points_count > 0:
                    status = "✅ Active"
                else:
                    status = "⚠️  Empty"
                
                table_data.append([
                    col.name,
                    system,
                    status,
                    points_count,
                    vector_size,
                    distance
                ])
                
            except Exception as e:
                logger.error(f"Error getting info for {col.name}: {e}")
                table_data.append([
                    col.name,
                    "❌ Error",
                    str(e),
                    "-",
                    "-",
                    "-"
                ])
        
        # Print table
        headers = ["Collection", "System", "Status", "Points", "Vector Size", "Distance"]
        logger.info(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Recommendations
        logger.info("\n" + "="*80)
        logger.info("💡 Recommendations")
        logger.info("="*80)
        
        expected_collections = [
            ("hotels_rag", "RAG system"),
            ("coupons_rag", "RAG coupons"),
            ("hotels_recommendation", "Recommendation system")
        ]
        
        existing_names = [col.name for col in collections.collections]
        
        for expected_name, description in expected_collections:
            if expected_name in existing_names:
                logger.info(f"✅ {expected_name}: OK ({description})")
            else:
                logger.info(f"⚠️  {expected_name}: MISSING ({description})")
        
        # Check for legacy collections
        legacy_collections = ["hotels", "hotel_recommendations"]
        found_legacy = [name for name in legacy_collections if name in existing_names]
        
        if found_legacy:
            logger.info("\n" + "-"*80)
            logger.info("⚠️  Legacy collections found:")
            for legacy in found_legacy:
                logger.info(f"  - {legacy}")
            logger.info("\nConsider migrating with: python scripts/migrate_collections.py --execute")
        
    except Exception as e:
        logger.error(f"❌ Error connecting to Qdrant: {e}")
        logger.info("\nMake sure Qdrant is running:")
        logger.info("  docker compose up -d qdrant")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Qdrant collections")
    parser.add_argument(
        "--url",
        default="http://localhost:6333",
        help="Qdrant server URL"
    )
    
    args = parser.parse_args()
    
    verify_collections(qdrant_url=args.url)

