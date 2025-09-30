#!/usr/bin/env python3
"""
Local Automation Connection Test
===============================

This script tests the automation connection system locally without database access.
It focuses on API endpoints and external service connectivity.

Usage:
    python3 local_automation_test.py
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "https://api.zimmerai.com"
SALES_AUTOMATION_BASE = "https://salesautomation.zimmerai.com/api"

async def test_api_endpoints():
    """Test API endpoints"""
    print("🚀 Local Automation Connection Test")
    print("=" * 50)
    
    issues = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Check main API health
        print("1. Testing main API health...")
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Main API is healthy")
            else:
                print(f"   ❌ Main API health check failed: {response.status_code}")
                issues.append("Main API health check failed")
        except Exception as e:
            print(f"   ❌ Main API error: {e}")
            issues.append("Main API not accessible")
        
        # Test 2: Check marketplace endpoint
        print("\n2. Testing marketplace endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/automations/marketplace")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                automations = data.get("automations", [])
                print(f"   ✅ Found {len(automations)} automations in marketplace")
                
                for automation in automations:
                    print(f"   - {automation.get('name')} (ID: {automation.get('id')})")
                    print(f"     Status: {automation.get('status')}, Listed: {automation.get('is_listed')}")
                    print(f"     Health: {automation.get('health_status')}")
                    print(f"     Base URL: {automation.get('api_base_url')}")
                    print(f"     Provision URL: {automation.get('api_provision_url')}")
                    
                    if not automation.get('api_provision_url'):
                        issues.append(f"Automation {automation.get('name')} missing provision URL")
            else:
                print(f"   ❌ Marketplace failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                issues.append("Marketplace endpoint failed")
        except Exception as e:
            print(f"   ❌ Marketplace error: {e}")
            issues.append("Marketplace endpoint error")
        
        # Test 3: Check sales automation endpoints
        print("\n3. Testing sales automation endpoints...")
        endpoints = {
            "base": f"{SALES_AUTOMATION_BASE}",
            "provision": f"{SALES_AUTOMATION_BASE}/zimmer/provision",
            "usage": f"{SALES_AUTOMATION_BASE}/zimmer/usage/consume",
            "kb_status": f"{SALES_AUTOMATION_BASE}/zimmer/kb/status",
            "kb_reset": f"{SALES_AUTOMATION_BASE}/zimmer/kb/reset"
        }
        
        for name, url in endpoints.items():
            try:
                print(f"   Testing {name}: {url}")
                response = await client.get(url)
                print(f"     Status: {response.status_code}")
                
                if response.status_code in [200, 404, 405]:  # 404/405 are OK for GET on POST endpoints
                    print(f"     ✅ {name} endpoint accessible")
                else:
                    print(f"     ❌ {name} endpoint failed: {response.status_code}")
                    print(f"     Response: {response.text[:100]}")
                    issues.append(f"Sales automation {name} endpoint failed")
                    
            except Exception as e:
                print(f"     ❌ {name} endpoint error: {e}")
                issues.append(f"Sales automation {name} endpoint error")
        
        # Test 4: Check other automation endpoints
        print("\n4. Testing other automation endpoints...")
        other_endpoints = [
            "/api/automations",
            "/api/automations/available"
        ]
        
        for endpoint in other_endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                print(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"     ✅ {endpoint} working")
                else:
                    print(f"     ❌ {endpoint} failed: {response.status_code}")
                    issues.append(f"Endpoint {endpoint} failed")
                    
            except Exception as e:
                print(f"     ❌ {endpoint} error: {e}")
                issues.append(f"Endpoint {endpoint} error")
        
        # Test 5: Check authentication endpoint
        print("\n5. Testing authentication endpoint...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "test@example.com", "password": "test"}
            )
            print(f"   Login endpoint: {response.status_code}")
            
            if response.status_code in [401, 422]:  # Expected for invalid credentials
                print("     ✅ Authentication endpoint working (expected 401/422)")
            else:
                print(f"     ⚠️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Authentication endpoint error: {e}")
            issues.append("Authentication endpoint error")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 Potential fixes:")
        print("   1. Check if automations have proper URLs configured")
        print("   2. Verify sales automation service is running")
        print("   3. Check API endpoint implementations")
        print("   4. Verify CORS settings")
    else:
        print("✅ All tests passed! No issues found.")
    
    return issues

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
