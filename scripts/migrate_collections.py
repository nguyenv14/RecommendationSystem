#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migrate Collections Script
Migrate from old collection names to new collection names
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_collections(qdrant_url: str = "http://localhost:6333", dry_run: bool = True):
    """
    Migrate collections from old names to new names
    
    Args:
        qdrant_url: Qdrant server URL
        dry_run: If True, only print what would be done
    """
    client = QdrantClient(url=qdrant_url)
    
    # Migration mapping
    migrations = [
        {
            "old": "hotels",
            "new": "hotels_rag",
            "description": "RAG system hotels collection"
        },
        {
            "old": "hotel_recommendations",
            "new": "hotels_recommendation",
            "description": "Recommendation system collection"
        }
    ]
    
    logger.info("="*60)
    logger.info("Collection Migration Script")
    logger.info("="*60)
    logger.info(f"Qdrant URL: {qdrant_url}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    logger.info("="*60)
    
    # Get existing collections
    try:
        collections = client.get_collections()
        existing_names = [col.name for col in collections.collections]
        logger.info(f"Existing collections: {existing_names}")
    except Exception as e:
        logger.error(f"Error getting collections: {e}")
        return
    
    logger.info("")
    logger.info("Migration Plan:")
    logger.info("-"*60)
    
    # Plan migrations
    actions = []
    for migration in migrations:
        old_name = migration["old"]
        new_name = migration["new"]
        description = migration["description"]
        
        old_exists = old_name in existing_names
        new_exists = new_name in existing_names
        
        logger.info(f"\n{description}")
        logger.info(f"  Old: {old_name} {'[EXISTS]' if old_exists else '[NOT FOUND]'}")
        logger.info(f"  New: {new_name} {'[EXISTS]' if new_exists else '[WILL BE CREATED]'}")
        
        if old_exists:
            if new_exists:
                logger.info(f"  Action: ⚠️  Both exist - will SKIP (manual merge needed)")
                actions.append(("skip", old_name, new_name, "Both collections exist"))
            else:
                logger.info(f"  Action: ✅ Will RENAME {old_name} → {new_name}")
                actions.append(("rename", old_name, new_name, description))
        else:
            if new_exists:
                logger.info(f"  Action: ✅ New collection already exists - OK")
                actions.append(("ok", old_name, new_name, "New collection exists"))
            else:
                logger.info(f"  Action: ℹ️  Neither exists - will CREATE empty {new_name}")
                actions.append(("create", old_name, new_name, description))
    
    logger.info("")
    logger.info("="*60)
    
    if dry_run:
        logger.info("⚠️  DRY RUN MODE - No changes will be made")
        logger.info("Run with --execute to perform migrations")
        return
    
    # Execute migrations
    logger.info("🚀 Executing migrations...")
    logger.info("="*60)
    
    for action_type, old_name, new_name, description in actions:
        try:
            if action_type == "rename":
                logger.info(f"\n📝 Renaming: {old_name} → {new_name}")
                
                # Get old collection info
                old_info = client.get_collection(old_name)
                vector_size = old_info.config.params.vectors.size
                distance = old_info.config.params.vectors.distance
                
                logger.info(f"  Vector size: {vector_size}")
                logger.info(f"  Distance: {distance}")
                logger.info(f"  Points: {old_info.points_count}")
                
                # Create new collection with same config
                client.create_collection(
                    collection_name=new_name,
                    vectors_config=VectorParams(size=vector_size, distance=distance)
                )
                logger.info(f"  ✅ Created new collection: {new_name}")
                
                # Get all points from old collection
                logger.info(f"  📦 Copying points...")
                offset = None
                batch_size = 100
                total_copied = 0
                
                while True:
                    points, offset = client.scroll(
                        collection_name=old_name,
                        limit=batch_size,
                        offset=offset
                    )
                    
                    if not points:
                        break
                    
                    # Upload to new collection
                    client.upsert(
                        collection_name=new_name,
                        points=points
                    )
                    total_copied += len(points)
                    logger.info(f"  Copied {total_copied} points...")
                    
                    if offset is None:
                        break
                
                logger.info(f"  ✅ Copied {total_copied} points")
                
                # Optionally delete old collection
                logger.info(f"  ⚠️  Keeping old collection {old_name} (delete manually if needed)")
                # client.delete_collection(old_name)  # Uncomment to auto-delete
                
            elif action_type == "create":
                logger.info(f"\n📝 Creating empty collection: {new_name}")
                # Create with default BGE-M3 size
                client.create_collection(
                    collection_name=new_name,
                    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
                )
                logger.info(f"  ✅ Created: {new_name}")
                
            elif action_type == "skip":
                logger.info(f"\n⚠️  Skipped: {old_name} → {new_name} ({description})")
                logger.info(f"  Both collections exist. Manual merge required.")
                
            elif action_type == "ok":
                logger.info(f"\n✅ OK: {new_name} already exists")
                
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
    
    logger.info("")
    logger.info("="*60)
    logger.info("✅ Migration completed!")
    logger.info("="*60)
    
    # Show final state
    collections = client.get_collections()
    logger.info("\nFinal collections:")
    for col in collections.collections:
        info = client.get_collection(col.name)
        logger.info(f"  - {col.name}: {info.points_count} points")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Qdrant collections")
    parser.add_argument(
        "--url",
        default="http://localhost:6333",
        help="Qdrant server URL"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute migrations (default: dry run)"
    )
    
    args = parser.parse_args()
    
    migrate_collections(
        qdrant_url=args.url,
        dry_run=not args.execute
    )

