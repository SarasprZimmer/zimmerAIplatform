#!/usr/bin/env python3
"""
Test different field name variations
"""
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_field_names():
    """Test different field name variations"""
    print("🧪 Testing Field Name Variations...")
    
    merchant_id = "eedc6cdf-b0f3-4936-8667-216e66593901"
    base_url = "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    
    # Test different field name variations
    field_variations = [
        {"merchant_id": merchant_id},
        {"MerchantID": merchant_id},
        {"merchantId": merchant_id},
        {"merchantid": merchant_id},
        {"merchant_id": merchant_id, "MerchantID": merchant_id},  # Try both
    ]
    
    for i, fields in enumerate(field_variations, 1):
        print(f"\n📝 Test {i}: Fields: {list(fields.keys())}")
        
        try:
            payload = {
                **fields,
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
    asyncio.run(test_field_names())
