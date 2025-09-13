#!/usr/bin/env python3
"""
Simple test to debug Zarinpal connection
"""
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_zarinpal_connection():
    """Test basic Zarinpal connection"""
    print("🧪 Testing Zarinpal Connection...")
    
    merchant_id = "eedc6cdf-b0f3-4936-8667-216e66593901"
    base_url = "https://sandbox.zarinpal.com/pg/rest/WebGate"
    
    print(f"Merchant ID: {merchant_id}")
    print(f"Base URL: {base_url}")
    
    # Test 1: Simple HTTP request to check if endpoint is reachable
    print("\n📝 Test 1: Basic HTTP Connection")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to reach the base URL
            response = await client.get(base_url)
            print(f"✅ Base URL reachable: {response.status_code}")
    except Exception as e:
        print(f"❌ Base URL not reachable: {e}")
    
    # Test 2: Try the actual payment request endpoint
    print("\n📝 Test 2: Payment Request Endpoint")
    try:
        payload = {
            "merchant_id": merchant_id,
            "amount": 100000,  # 100,000 Rial
            "description": "Test Payment",
            "callback_url": "https://example.com/callback",
            "metadata": {}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/PaymentRequest.json",
                json=payload
            )
            
            print(f"✅ Payment request response: {response.status_code}")
            print(f"Response body: {response.text}")
            
    except Exception as e:
        print(f"❌ Payment request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_zarinpal_connection())
