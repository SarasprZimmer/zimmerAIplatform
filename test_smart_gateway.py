#!/usr/bin/env python3
"""
Test Smart Gateway System
========================

This script tests the smart gateway URL validation and service token generation
functionality.

Usage:
    python3 test_smart_gateway.py
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test URLs (you can replace these with actual automation URLs)
TEST_URLS = {
    "api_base_url": "https://salesautomation.zimmerai.com/api/",
    "api_provision_url": "https://salesautomation.zimmerai.com/api/zimmer/provision",
    "api_usage_url": "https://salesautomation.zimmerai.com/api/zimmer/usage/consume",
    "api_kb_status_url": "https://salesautomation.zimmerai.com/api/zimmer/kb/status",
    "api_kb_reset_url": "https://salesautomation.zimmerai.com/api/zimmer/kb/reset"
}

async def test_url_validation():
    """Test the URL validation endpoint"""
    print("🔍 Testing URL Validation...")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test URL validation
            response = await client.post(
                "https://api.zimmerai.com/api/admin/automations/validate-urls",
                json=TEST_URLS,
                headers={
                    "Authorization": "Bearer YOUR_ADMIN_TOKEN",  # Replace with actual token
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ URL Validation Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Check if all URLs are valid
                if data.get("can_generate_token"):
                    print("\n🎉 All URLs are valid! Can generate service token.")
                else:
                    print("\n⚠️ Some URLs are invalid. Cannot generate service token.")
                    
            else:
                print(f"❌ URL Validation Failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing URL validation: {e}")

async def test_service_token_generation():
    """Test the service token generation endpoint"""
    print("\n🔑 Testing Service Token Generation...")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test service token generation (replace 1 with actual automation ID)
            response = await client.post(
                "https://api.zimmerai.com/api/admin/automations/1/generate-service-token",
                headers={
                    "Authorization": "Bearer YOUR_ADMIN_TOKEN",  # Replace with actual token
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Service Token Generated:")
                print(f"Token: {data.get('service_token', 'N/A')}")
                print(f"Automation ID: {data.get('automation_id', 'N/A')}")
                print(f"Message: {data.get('message', 'N/A')}")
                
                # Show integration instructions
                instructions = data.get('instructions', {})
                if instructions:
                    print("\n📋 Integration Instructions:")
                    for step in instructions.get('integration_steps', []):
                        print(f"  {step}")
                        
            else:
                print(f"❌ Service Token Generation Failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing service token generation: {e}")

async def test_individual_urls():
    """Test individual URLs directly"""
    print("\n🌐 Testing Individual URLs...")
    print("=" * 50)
    
    for url_type, url in TEST_URLS.items():
        print(f"\nTesting {url_type}: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code in [200, 404, 405]:
                    print(f"  ✅ Status: {response.status_code}")
                    print(f"  📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
                    print(f"  📏 Response Size: {len(response.content)} bytes")
                else:
                    print(f"  ❌ Status: {response.status_code} - {response.reason_phrase}")
                    
        except httpx.TimeoutException:
            print(f"  ⏰ Timeout - URL may be unreachable")
        except httpx.ConnectError:
            print(f"  🔌 Connection Error - URL may be invalid or server down")
        except Exception as e:
            print(f"  ❌ Error: {e}")

async def main():
    """Main test function"""
    print("🚀 Smart Gateway System Test")
    print("=" * 50)
    print("This script tests the smart gateway URL validation and service token generation.")
    print("Make sure to replace 'YOUR_ADMIN_TOKEN' with a valid admin token.")
    print()
    
    # Test individual URLs first
    await test_individual_urls()
    
    # Test URL validation endpoint
    await test_url_validation()
    
    # Test service token generation
    await test_service_token_generation()
    
    print("\n🎯 Test Summary:")
    print("=" * 50)
    print("1. Individual URL tests show basic connectivity")
    print("2. URL validation endpoint provides comprehensive validation")
    print("3. Service token generation creates secure tokens for automation")
    print("\n💡 Next Steps:")
    print("- Replace 'YOUR_ADMIN_TOKEN' with actual admin token")
    print("- Test with real automation URLs")
    print("- Integrate service tokens into automation services")

if __name__ == "__main__":
    asyncio.run(main())
