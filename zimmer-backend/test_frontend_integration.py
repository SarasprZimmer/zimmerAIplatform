#!/usr/bin/env python3
"""
Test script to verify frontend integration with new authentication system
"""
import asyncio
import httpx
import json
from datetime import datetime


# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@zimmer.com"
TEST_PASSWORD = "admin123"


async def test_frontend_integration():
    """Test the complete frontend integration flow"""
    print("🧪 Testing Frontend Integration")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Test login (simulates frontend login)
        print("1️⃣ Testing Login (Frontend Simulation)")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                cookies = response.cookies
                
                print(f"✅ Login successful")
                print(f"   Access token: {data['access_token'][:30]}...")
                print(f"   User: {data['user']['name']} ({data['user']['email']})")
                print(f"   Is admin: {data['user']['is_admin']}")
                print(f"   Refresh token cookie: {cookies.get('refresh_token', 'NOT SET')[:30]}...")
                
                access_token = data['access_token']
                user_data = data['user']
                
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        # Step 2: Test user info endpoint (simulates frontend API call)
        print("\n2️⃣ Testing User Info Endpoint")
        try:
            response = await client.get(
                f"{BASE_URL}/api/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ User info retrieved successfully")
                print(f"   User ID: {user_info['id']}")
                print(f"   Name: {user_info['name']}")
                print(f"   Email: {user_info['email']}")
            else:
                print(f"❌ User info failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ User info error: {e}")
        
        # Step 3: Test dashboard endpoint (simulates frontend dashboard)
        print("\n3️⃣ Testing Dashboard Endpoint")
        try:
            response = await client.get(
                f"{BASE_URL}/api/user/dashboard",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                dashboard_data = response.json()
                print(f"✅ Dashboard data retrieved successfully")
                print(f"   User: {dashboard_data['user']['name']}")
                print(f"   Total demo tokens: {dashboard_data.get('total_demo_tokens', 0)}")
                print(f"   Total paid tokens: {dashboard_data.get('total_paid_tokens', 0)}")
                print(f"   Automations count: {len(dashboard_data.get('automations', []))}")
            else:
                print(f"❌ Dashboard failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
        
        # Step 4: Test token refresh (simulates automatic refresh)
        print("\n4️⃣ Testing Token Refresh")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/refresh",
                cookies=cookies
            )
            
            if response.status_code == 200:
                refresh_data = response.json()
                new_cookies = response.cookies
                print(f"✅ Token refresh successful")
                print(f"   New access token: {refresh_data['access_token'][:30]}...")
                print(f"   New refresh token: {new_cookies.get('refresh_token', 'NOT SET')[:30]}...")
                
                # Update access token for next tests
                access_token = refresh_data['access_token']
                cookies = new_cookies
                
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
        
        # Step 5: Test API call with refreshed token
        print("\n5️⃣ Testing API Call with Refreshed Token")
        try:
            response = await client.get(
                f"{BASE_URL}/api/user/automations",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                automations = response.json()
                print(f"✅ Automations retrieved successfully")
                print(f"   Automations count: {len(automations)}")
                for automation in automations[:3]:  # Show first 3
                    print(f"   - {automation.get('name', 'Unknown')} (ID: {automation.get('id')})")
            else:
                print(f"❌ Automations failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Automations error: {e}")
        
        # Step 6: Test logout (simulates frontend logout)
        print("\n6️⃣ Testing Logout")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/logout",
                cookies=cookies
            )
            
            if response.status_code == 200:
                logout_data = response.json()
                new_cookies = response.cookies
                print(f"✅ Logout successful: {logout_data['message']}")
                print(f"   Refresh token cleared: {'refresh_token' not in new_cookies}")
            else:
                print(f"❌ Logout failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Logout error: {e}")
        
        # Step 7: Test API call after logout (should fail)
        print("\n7️⃣ Testing API Call After Logout")
        try:
            response = await client.get(
                f"{BASE_URL}/api/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 401:
                print(f"✅ API call correctly rejected after logout (401)")
            else:
                print(f"⚠️  API call should have been rejected but got: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Post-logout API error: {e}")


async def test_cors_headers():
    """Test CORS headers for frontend integration"""
    print("\n🌐 Testing CORS Headers")
    print("=" * 30)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test preflight request
            response = await client.options(
                f"{BASE_URL}/api/auth/login",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            print(f"CORS preflight status: {response.status_code}")
            print(f"Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
            print(f"Access-Control-Allow-Credentials: {response.headers.get('access-control-allow-credentials')}")
            print(f"Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
            
        except Exception as e:
            print(f"❌ CORS test error: {e}")


if __name__ == "__main__":
    print("🔧 Frontend Integration Test Suite")
    print("Make sure the backend server is running on http://localhost:8000")
    print("Make sure you have a test user with email: admin@zimmer.com")
    print()
    
    try:
        asyncio.run(test_frontend_integration())
        asyncio.run(test_cors_headers())
        
        print("\n" + "=" * 50)
        print("🎉 Frontend integration tests completed!")
        print("\n📋 Next steps:")
        print("  1. Start your frontend applications")
        print("  2. Test login with the new authentication system")
        print("  3. Verify automatic token refresh works")
        print("  4. Test logout functionality")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
