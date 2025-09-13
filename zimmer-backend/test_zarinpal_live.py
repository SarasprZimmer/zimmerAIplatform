#!/usr/bin/env python3
"""
Test Zarinpal live endpoints to see if they work
"""
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_zarinpal_live():
    """Test Zarinpal live endpoints"""
    print("🧪 Testing Zarinpal Live Endpoints...")
    
    merchant_id = "eedc6cdf-b0f3-4936-8667-216e66593901"
    
    # Test live Zarinpal URLs
    test_urls = [
        "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json",
        "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest",
        "https://www.zarinpal.com/pg/rest/WebGate",
    ]
    
    for i, base_url in enumerate(test_urls, 1):
        print(f"\n📝 Test {i}: {base_url}")
        
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
                    base_url,
                    json=payload
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code != 404:
                    print(f"   Response: {response.text[:200]}...")
                else:
                    print(f"   Response: 404 Not Found")
                    
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_zarinpal_live())
