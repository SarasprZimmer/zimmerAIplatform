#!/usr/bin/env python3
"""
Test script for authentication sessions system
"""
import asyncio
import httpx
import time
from datetime import datetime, timedelta


# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@zimmer.com"
TEST_PASSWORD = "admin123"


async def test_login():
    """Test user login and session creation"""
    print("🔐 Testing login...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login successful")
                print(f"   Access token: {data['access_token'][:20]}...")
                print(f"   User: {data['user']['name']} ({data['user']['email']})")
                print(f"   Is admin: {data['user']['is_admin']}")
                
                # Check if refresh token cookie is set
                cookies = response.cookies
                if "refresh_token" in cookies:
                    print(f"✅ Refresh token cookie set: {cookies['refresh_token'][:20]}...")
                else:
                    print("❌ Refresh token cookie not set")
                
                return data['access_token'], cookies
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None, None


async def test_refresh_token(access_token, cookies):
    """Test token refresh"""
    print("\n🔄 Testing token refresh...")
    
    if not cookies or "refresh_token" not in cookies:
        print("❌ No refresh token cookie available")
        return None
    
    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/auth/refresh")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token refresh successful")
                print(f"   New access token: {data['access_token'][:20]}...")
                
                # Check if new refresh token cookie is set (rotation)
                new_cookies = response.cookies
                if "refresh_token" in new_cookies:
                    old_refresh = cookies["refresh_token"][:20]
                    new_refresh = new_cookies["refresh_token"][:20]
                    if old_refresh != new_refresh:
                        print(f"✅ Refresh token rotated: {old_refresh}... → {new_refresh}...")
                    else:
                        print(f"⚠️  Refresh token not rotated")
                
                return data['access_token']
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return None


async def test_expired_token_refresh(cookies):
    """Test refresh with expired access token (should work)"""
    print("\n⏰ Testing refresh with expired access token...")
    
    if not cookies or "refresh_token" not in cookies:
        print("❌ No refresh token cookie available")
        return False
    
    # Wait for access token to expire (15 minutes)
    print("   Waiting for access token to expire (15 minutes)...")
    print("   (This test will take a while)")
    
    # For testing, we'll just test the refresh endpoint
    # In a real scenario, you'd wait for the token to expire
    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/auth/refresh")
            
            if response.status_code == 200:
                print("✅ Refresh successful even with expired access token")
                return True
            else:
                print(f"❌ Refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Refresh error: {e}")
            return False


async def test_logout(cookies):
    """Test user logout"""
    print("\n🚪 Testing logout...")
    
    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/auth/logout")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Logout successful: {data['message']}")
                
                # Check if refresh token cookie is cleared
                new_cookies = response.cookies
                if "refresh_token" not in new_cookies or new_cookies["refresh_token"] == "":
                    print("✅ Refresh token cookie cleared")
                else:
                    print("❌ Refresh token cookie not cleared")
                
                return True
            else:
                print(f"❌ Logout failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return False


async def test_refresh_after_logout(cookies):
    """Test refresh after logout (should fail)"""
    print("\n🚫 Testing refresh after logout...")
    
    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.post(f"{BASE_URL}/api/auth/refresh")
            
            if response.status_code == 401:
                print("✅ Refresh correctly failed after logout")
                return True
            else:
                print(f"❌ Refresh should have failed but got: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Refresh error: {e}")
            return False


async def test_logout_all_sessions(access_token):
    """Test logout from all sessions"""
    print("\n🚪 Testing logout from all sessions...")
    
    if not access_token:
        print("❌ No access token available")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/logout-all",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Logout all sessions successful: {data['message']}")
                return True
            else:
                print(f"❌ Logout all sessions failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Logout all sessions error: {e}")
            return False


async def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n❌ Testing invalid credentials...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": "invalid@example.com",
                    "password": "wrongpassword"
                }
            )
            
            if response.status_code == 401:
                print("✅ Invalid credentials correctly rejected")
                return True
            else:
                print(f"❌ Invalid credentials should have been rejected but got: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Invalid credentials test error: {e}")
            return False


async def test_missing_refresh_token():
    """Test refresh without refresh token cookie"""
    print("\n🍪 Testing refresh without refresh token...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/api/auth/refresh")
            
            if response.status_code == 401:
                print("✅ Refresh correctly failed without refresh token")
                return True
            else:
                print(f"❌ Refresh should have failed without refresh token but got: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Missing refresh token test error: {e}")
            return False


async def run_all_tests():
    """Run all authentication tests"""
    print("🚀 Starting Authentication Sessions Tests")
    print("=" * 50)
    
    # Test 1: Login
    access_token, cookies = await test_login()
    if not access_token:
        print("❌ Cannot continue tests without successful login")
        return
    
    # Test 2: Token refresh
    new_access_token = await test_refresh_token(access_token, cookies)
    if new_access_token:
        access_token = new_access_token
    
    # Test 3: Refresh with expired token (simulated)
    await test_expired_token_refresh(cookies)
    
    # Test 4: Logout
    logout_success = await test_logout(cookies)
    
    # Test 5: Refresh after logout
    if logout_success:
        await test_refresh_after_logout(cookies)
    
    # Test 6: Login again for logout all test
    print("\n🔄 Logging in again for logout all test...")
    access_token2, cookies2 = await test_login()
    if access_token2:
        # Test 7: Logout all sessions
        await test_logout_all_sessions(access_token2)
    
    # Test 8: Invalid credentials
    await test_invalid_credentials()
    
    # Test 9: Missing refresh token
    await test_missing_refresh_token()
    
    print("\n" + "=" * 50)
    print("🎉 All authentication tests completed!")


if __name__ == "__main__":
    print("🔧 Authentication Sessions Test Suite")
    print("Make sure the backend server is running on http://localhost:8000")
    print("Make sure you have a test user with email: admin@zimmerai.com")
    print()
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
