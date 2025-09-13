#!/usr/bin/env python3
"""
Test the payment API endpoints
"""
import asyncio
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_payment_api():
    """Test the payment API endpoints"""
    print("🧪 Testing Payment API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Login to get access token
    print("\n📝 Test 1: User Authentication")
    try:
        async with httpx.AsyncClient() as client:
            # Login
            login_data = {
                "email": "test@example.com",
                "password": "test123"
            }
            
            login_response = await client.post(
                f"{base_url}/api/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data["access_token"]
                print(f"✅ Login successful, got access token")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return
                
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return
    
    # Test 2: Get available automations
    print("\n📝 Test 2: Get Available Automations")
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            automations_response = await client.get(
                f"{base_url}/api/automations/available",
                headers=headers
            )
            
            if automations_response.status_code == 200:
                automations = automations_response.json()
                print(f"✅ Got {len(automations)} automations")
                
                # Debug: print the first automation to see its structure
                if automations:
                    print(f"   First automation: {automations[0]}")
                
                # Find an automation to test with (the available endpoint already filters for healthy/listed)
                test_automation = automations[0] if automations else None
                
                if test_automation:
                    print(f"✅ Found test automation: {test_automation['name']}")
                    print(f"   Price per token: {test_automation['price_per_token']}")
                    print(f"   Pricing type: {test_automation['pricing_type']}")
                else:
                    print("❌ No suitable automation found for testing")
                    return
            else:
                print(f"❌ Failed to get automations: {automations_response.status_code}")
                return
                
    except Exception as e:
        print(f"❌ Automations test failed: {e}")
        return
    
    # Test 3: Initialize Payment
    print("\n📝 Test 3: Initialize Payment")
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            payment_data = {
                "automation_id": test_automation["id"],
                "tokens": 100,  # 100 tokens
                "return_path": "/payment/success"
            }
            
            payment_response = await client.post(
                f"{base_url}/api/payments/zarinpal/init",
                json=payment_data,
                headers=headers
            )
            
            if payment_response.status_code in [200, 201]:
                payment_result = payment_response.json()
                print(f"✅ Payment initialized successfully:")
                print(f"   Payment ID: {payment_result['payment_id']}")
                print(f"   Authority: {payment_result['authority']}")
                print(f"   Redirect URL: {payment_result['redirect_url']}")
                
                # Store for verification test
                payment_id = payment_result['payment_id']
                authority = payment_result['authority']
                
            else:
                print(f"❌ Payment initialization failed: {payment_response.status_code}")
                print(f"   Response: {payment_response.text}")
                return
                
    except Exception as e:
        print(f"❌ Payment initialization test failed: {e}")
        return
    
    # Test 4: Simulate Payment Callback
    print("\n📝 Test 4: Payment Callback (Simulated)")
    try:
        async with httpx.AsyncClient() as client:
            # Simulate successful payment callback
            callback_url = f"{base_url}/api/payments/zarinpal/callback"
            params = {
                "payment_id": payment_id,
                "Authority": authority,
                "Status": "OK"
            }
            
            callback_response = await client.get(callback_url, params=params)
            
            if callback_response.status_code in [200, 201, 204]:
                callback_result = callback_response.json()
                print(f"✅ Payment callback processed:")
                print(f"   Status: {callback_result.get('status')}")
                print(f"   Ref ID: {callback_result.get('ref_id')}")
                print(f"   Message: {callback_result.get('message')}")
            else:
                print(f"❌ Payment callback failed: {callback_response.status_code}")
                print(f"   Response: {callback_response.text}")
                
    except Exception as e:
        print(f"❌ Payment callback test failed: {e}")
        return
    
    print("\n🎉 Payment API tests completed!")

if __name__ == "__main__":
    asyncio.run(test_payment_api())
