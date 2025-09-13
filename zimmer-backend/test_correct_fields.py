#!/usr/bin/env python3
"""
Test with correct capitalized field names
"""
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.payments")

async def test_correct_fields():
    """Test with correct field names"""
    print("🧪 Testing with Correct Field Names...")
    
    merchant_id = "eedc6cdf-b0f3-4936-8667-216e66593901"
    base_url = "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    
    try:
        payload = {
            "MerchantID": merchant_id,
            "Amount": 100000,  # 100,000 Rial
            "Description": "Test Payment - Zimmer AI Automation",
            "CallbackURL": "https://example.com/callback",
            "Metadata": {}
        }
        
        print(f"Payload: {payload}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                base_url,
                json=payload
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                print(f"Response: {response_data}")
                
                if response_data.get("Status") == 100:
                    print(f"✅ SUCCESS! Authority: {response_data.get('Authority')}")
                    print(f"   Payment URL: https://www.zarinpal.com/pg/StartPay/{response_data.get('Authority')}")
                else:
                    print(f"❌ Failed: {response_data.get('errors', response_data)}")
            else:
                print(f"Response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_correct_fields())
