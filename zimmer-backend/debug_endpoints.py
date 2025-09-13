#!/usr/bin/env python3
"""
Debug script to test failing endpoints and see actual responses
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method="GET", data=None):
    """Test an endpoint and show detailed response"""
    print(f"\n🔍 Testing {name}: {method} {url}")
    print("-" * 60)
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Endpoint accessible")
        elif response.status_code == 401:
            print("✅ Endpoint properly secured (401 Unauthorized)")
        elif response.status_code == 403:
            print("✅ Endpoint properly secured (403 Forbidden)")
        elif response.status_code == 404:
            print("❌ Endpoint not found")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("-" * 60)

def main():
    """Test all the failing endpoints"""
    print("🚀 Debugging Zimmer Platform Endpoints")
    print("=" * 60)
    
    # Test the failing endpoints
    test_endpoint("Public Automations", f"{BASE_URL}/api/automations/available")
    test_endpoint("Protected Endpoints", f"{BASE_URL}/api/me")
    test_endpoint("Admin Endpoints", f"{BASE_URL}/api/admin/users")
    test_endpoint("Notification Endpoints", f"{BASE_URL}/api/notifications")
    
    # Test some working endpoints for comparison
    print("\n" + "=" * 60)
    print("🔍 Testing Working Endpoints for Comparison")
    print("=" * 60)
    
    test_endpoint("Health Check", f"{BASE_URL}/health")
    test_endpoint("Public Knowledge", f"{BASE_URL}/api/knowledge")
    test_endpoint("Payment Endpoints", f"{BASE_URL}/api/payments/zarinpal/init", "POST", {"automation_id": 1, "tokens": 100})

if __name__ == "__main__":
    main()
