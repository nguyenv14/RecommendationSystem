#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Hotel Recommendation API
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")

def test_add_hotel():
    """Test adding a new hotel"""
    print("2. Testing add hotel...")
    
    hotel_data = {
        "hotel_id": 999,
        "hotel_name": "Test Luxury Resort",
        "hotel_desc": "A beautiful test hotel for API testing",
        "hotel_placedetails": "Test Location, Vietnam",
        "hotel_tag_keyword": "luxury, test, resort",
        "hotel_rank": 5,
        "hotel_price_average": 5000000
    }
    
    response = requests.post(
        f"{BASE_URL}/api/hotels/process",
        json=hotel_data
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")

def test_get_similar():
    """Test getting similar hotels"""
    print("3. Testing get similar hotels...")
    
    hotel_id = 2
    top_k = 5
    response = requests.get(
        f"{BASE_URL}/api/hotels/{hotel_id}/similar?top_k={top_k}"
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Hotel ID: {data['hotel_id']}")
    print(f"   Recommendations: {len(data['recommendations'])}")
    for rec in data['recommendations']:
        print(f"     - {rec['hotel_name']}: {rec['cosine_similarity']:.4f}")

def test_search():
    """Test search by query"""
    print("\n4. Testing search...")
    
    query_data = {
        "query": "Khách sạn gần biển",
        "top_k": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/hotels/search",
        json=query_data
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Query: {data['query']}")
    print(f"   Results: {len(data['results'])}")
    for result in data['results'][:3]:
        print(f"     - {result['hotel_name']}: {result['similarity_score']:.4f}")

def test_collection_info():
    """Test getting collection info"""
    print("\n5. Testing collection info...")
    
    response = requests.get(f"{BASE_URL}/api/hotels/info")
    print(f"   Status: {response.status_code}")
    print(f"   Info: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Hotel Recommendation API Tests")
    print("=" * 60 + "\n")
    
    try:
        test_health_check()
        test_add_hotel()
        test_get_similar()
        test_search()
        test_collection_info()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API service")
        print("   Make sure the service is running:")
        print("   python api_service.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()

