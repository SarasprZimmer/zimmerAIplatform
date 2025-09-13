#!/usr/bin/env python3
"""
Debug script to investigate refresh token issues
"""
import asyncio
import httpx
import json
from datetime import datetime


# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@zimmer.com"
TEST_PASSWORD = "admin123"


async def debug_refresh_issue():
    """Debug the refresh token issue step by step"""
    print("🔍 Debugging Refresh Token Issue")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login and get initial tokens
        print("1️⃣ Step 1: Login")
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        login_data = login_response.json()
        cookies = login_response.cookies
        
        print(f"✅ Login successful")
        print(f"   Access token: {login_data['access_token'][:30]}...")
        print(f"   Refresh token cookie: {cookies.get('refresh_token', 'NOT SET')[:30]}...")
        
        # Step 2: Try refresh immediately
        print("\n2️⃣ Step 2: Immediate refresh")
        refresh_response = None
        try:
            refresh_response = await client.post(
                f"{BASE_URL}/api/auth/refresh",
                cookies=cookies
            )
            
            print(f"Refresh status: {refresh_response.status_code}")
            if refresh_response.status_code == 200:
                refresh_data = refresh_response.json()
                new_cookies = refresh_response.cookies
                print(f"✅ Refresh successful")
                print(f"   New access token: {refresh_data['access_token'][:30]}...")
                print(f"   New refresh token: {new_cookies.get('refresh_token', 'NOT SET')[:30]}...")
                
                # Check if tokens rotated
                old_refresh = cookies.get('refresh_token', '')[:20]
                new_refresh = new_cookies.get('refresh_token', '')[:20]
                if old_refresh != new_refresh:
                    print(f"✅ Refresh token rotated: {old_refresh}... → {new_refresh}...")
                else:
                    print(f"⚠️  Refresh token not rotated")
                    
            else:
                print(f"❌ Refresh failed: {refresh_response.text}")
                
        except Exception as e:
            print(f"❌ Refresh error: {e}")
        
        # Step 3: Try refresh again with new cookies
        print("\n3️⃣ Step 3: Second refresh")
        try:
            # Use the new cookies from the previous refresh
            if refresh_response and 'refresh_token' in refresh_response.cookies:
                second_refresh_response = await client.post(
                    f"{BASE_URL}/api/auth/refresh",
                    cookies=refresh_response.cookies
                )
                
                print(f"Second refresh status: {second_refresh_response.status_code}")
                if second_refresh_response.status_code == 200:
                    print("✅ Second refresh successful")
                else:
                    print(f"❌ Second refresh failed: {second_refresh_response.text}")
            else:
                print("⚠️  No refresh token cookie available for second refresh")
                
        except Exception as e:
            print(f"❌ Second refresh error: {e}")
        
        # Step 4: Check database state
        print("\n4️⃣ Step 4: Database state check")
        try:
            # Use the access token to check user info
            user_response = await client.get(
                f"{BASE_URL}/api/users/me",
                headers={"Authorization": f"Bearer {login_data['access_token']}"}
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(f"✅ User info retrieved: {user_data['email']}")
            else:
                print(f"❌ User info failed: {user_response.status_code}")
                
        except Exception as e:
            print(f"❌ User info error: {e}")


async def test_concurrent_refresh():
    """Test concurrent refresh requests"""
    print("\n🔄 Testing Concurrent Refresh")
    print("=" * 30)
    
    async with httpx.AsyncClient() as client:
        # Login first
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed for concurrent test")
            return
        
        cookies = login_response.cookies
        
        # Make multiple concurrent refresh requests
        tasks = []
        for i in range(3):
            task = client.post(
                f"{BASE_URL}/api/auth/refresh",
                cookies=cookies
            )
            tasks.append(task)
        
        print("Making 3 concurrent refresh requests...")
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i+1}: ❌ Error - {response}")
            elif response.status_code == 200:
                print(f"Request {i+1}: ✅ Success")
            else:
                print(f"Request {i+1}: ❌ Failed - {response.status_code}")


if __name__ == "__main__":
    print("🔧 Refresh Token Debug Script")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        asyncio.run(debug_refresh_issue())
        asyncio.run(test_concurrent_refresh())
    except KeyboardInterrupt:
        print("\n⏹️  Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug error: {e}")
