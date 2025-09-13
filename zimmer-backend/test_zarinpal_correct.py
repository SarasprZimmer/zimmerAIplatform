#!/usr/bin/env python3
"""
Test with correct Zarinpal sandbox endpoints
"""
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_zarinpal_correct():
    """Test with correct Zarinpal endpoints"""
    print("🧪 Testing Zarinpal with Correct Endpoints...")
    
    merchant_id = "eedc6cdf-b0f3-4936-8667-216e66593901"
    
    # Test different possible Zarinpal sandbox URLs
    test_urls = [
        "https://sandbox.zarinpal.com/pg/rest/WebGate",
        "https://sandbox.zarinpal.com/pg/rest/WebGate/",
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json",
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest",
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json/",
        "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest/",
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
    asyncio.run(test_zarinpal_correct())
