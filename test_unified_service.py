#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Unified Service (RAG + Recommendation)
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_URL = "http://localhost:5000"
TIMEOUT = 30

def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(response: requests.Response):
    """Print formatted response"""
    try:
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    print_header("1. Testing Health Check")
    try:
        response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_status():
    """Test status endpoint"""
    print_header("2. Testing Status Endpoint")
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=TIMEOUT)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rag_chat():
    """Test RAG chat endpoint"""
    print_header("3. Testing RAG Chat")
    try:
        data = {
            "question": "Khách sạn nào ở Nha Trang có spa và hồ bơi?"
        }
        response = requests.post(
            f"{API_URL}/api/chat",
            json=data,
            timeout=TIMEOUT
        )
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rag_search():
    """Test RAG search endpoint"""
    print_header("4. Testing RAG Search")
    try:
        data = {
            "query": "khách sạn 5 sao gần biển",
            "top_k": 5
        }
        response = requests.post(
            f"{API_URL}/api/search",
            json=data,
            timeout=TIMEOUT
        )
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_hotel_search():
    """Test hotel search (Recommendation)"""
    print_header("5. Testing Hotel Search (Recommendation)")
    try:
        data = {
            "query": "khách sạn 5 sao có spa",
            "top_k": 5
        }
        response = requests.post(
            f"{API_URL}/api/hotels/search",
            json=data,
            timeout=TIMEOUT
        )
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_similar_hotels():
    """Test similar hotels endpoint"""
    print_header("6. Testing Similar Hotels")
    try:
        hotel_id = 1
        response = requests.get(
            f"{API_URL}/api/hotels/{hotel_id}/similar?top_k=5",
            timeout=TIMEOUT
        )
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_collection_info():
    """Test collection info endpoint"""
    print_header("7. Testing Collection Info")
    try:
        response = requests.get(
            f"{API_URL}/api/hotels/info",
            timeout=TIMEOUT
        )
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "UNIFIED SERVICE TEST SUITE" + " "*17 + "║")
    print("╚" + "═"*58 + "╝")
    
    print(f"\n🔗 API URL: {API_URL}")
    print(f"⏱️  Timeout: {TIMEOUT}s")
    
    # Check if service is running
    print_header("Checking if service is running...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Service is not running or unhealthy!")
            print("\nPlease start the service first:")
            print("  Linux/Mac: ./run_unified_service.sh")
            print("  Windows:   run_unified_service.bat")
            sys.exit(1)
        print("✅ Service is running!")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to service!")
        print(f"\nMake sure the service is running on {API_URL}")
        print("\nStart with:")
        print("  Linux/Mac: ./run_unified_service.sh")
        print("  Windows:   run_unified_service.bat")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Status", test_status),
        ("RAG Chat", test_rag_chat),
        ("RAG Search", test_rag_search),
        ("Hotel Search", test_hotel_search),
        ("Similar Hotels", test_similar_hotels),
        ("Collection Info", test_collection_info),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print()
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print("\n" + "="*60 + "\n")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

