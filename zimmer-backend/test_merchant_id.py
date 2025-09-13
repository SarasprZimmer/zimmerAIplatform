#!/usr/bin/env python3
"""
Test merchant ID formatting
"""
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_merchant_id():
    """Test different merchant ID formats"""
    print("🧪 Testing Merchant ID Formats...")
    
    # Test different formats of the merchant ID
    merchant_ids = [
        "eedc6cdf-b0f3-4936-8667-216e66593901",  # Original
        "eedc6cdf-b0f3-4936-8667-216e66593901".strip(),  # Stripped
        "eedc6cdf-b0f3-4936-8667-216e66593901".replace("-", ""),  # No hyphens
        "eedc6cdfb0f349368667216e66593901",  # No hyphens
    ]
    
    base_url = "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    
    for i, merchant_id in enumerate(merchant_ids, 1):
        print(f"\n📝 Test {i}: Merchant ID: '{merchant_id}'")
        
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
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    
                    if response_data.get("Status") == 100:
                        print(f"   ✅ SUCCESS! Authority: {response_data.get('Authority')}")
                    else:
                        print(f"   ❌ Failed: {response_data.get('errors', response_data)}")
                else:
                    print(f"   Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_merchant_id())
