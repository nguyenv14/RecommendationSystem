#!/usr/bin/env python3
"""Check what's stored in Qdrant"""

from qdrant_client import QdrantClient

client = QdrantClient(url='http://localhost:6333')

# Get all points for hotel 2
results = client.scroll(
    collection_name="hotel_recommendations",
    limit=100
)

print(f"Total points in collection: {len(results[0])}")
print(f"\nFirst 10 points:")
for i, point in enumerate(results[0][:10], 1):
    print(f"\n{i}. ID: {point.id}")
    print(f"   Payload: {point.payload}")
    if point.vector:
        print(f"   Vector shape: {len(point.vector)}")
    else:
        print(f"   Vector: None")

# Check hotel IDs distribution
print("\n" + "="*60)
print("Hotel ID distribution:")
hotel_counts = {}
for point in results[0]:
    hotel_id = point.payload.get('hotel_id', 'unknown')
    hotel_counts[hotel_id] = hotel_counts.get(hotel_id, 0) + 1

for hotel_id, count in sorted(hotel_counts.items()):
    print(f"Hotel ID {hotel_id}: {count} chunks")

