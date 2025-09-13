"""
Zarinpal payment gateway client
"""
import uuid
import json
import httpx
from typing import Dict, Optional, Union
from enum import Enum


class PaymentMode(str, Enum):
    MOCK = "mock"
    SANDBOX = "sandbox"
    LIVE = "live"


class ZarinpalClient:
    """
    Zarinpal payment gateway client supporting mock, sandbox, and live modes
    """
    
    def __init__(self, merchant_id: str, base_url: str, mode: PaymentMode = PaymentMode.MOCK):
        self.merchant_id = merchant_id
        self.base_url = base_url
        self.mode = mode
        
        # Mock mode configuration
        if mode == PaymentMode.MOCK:
            self.base_url = "https://mock.zarinpal"
    
    async def request_payment(
        self, 
        amount_rial: int, 
        description: str, 
        callback_url: str, 
        email: Optional[str] = None, 
        mobile: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Request payment from Zarinpal
        
        Args:
            amount_rial: Amount in Rial (integer)
            description: Payment description
            callback_url: Return URL after payment
            email: Customer email (optional)
            mobile: Customer mobile (optional)
            
        Returns:
            Dict with 'authority' and 'url' keys
        """
        if self.mode == PaymentMode.MOCK:
            return self._mock_request_payment(amount_rial, description, callback_url)
        else:
            return await self._real_request_payment(amount_rial, description, callback_url, email, mobile)
    
    async def verify_payment(self, authority: str, amount_rial: int) -> Dict[str, Union[bool, str, int]]:
        """
        Verify payment with Zarinpal
        
        Args:
            authority: Payment authority from request
            amount_rial: Original amount in Rial
            
        Returns:
            Dict with 'ok', 'ref_id', 'code', 'message' keys
        """
        if self.mode == PaymentMode.MOCK:
            return self._mock_verify_payment(authority, amount_rial)
        else:
            return await self._real_verify_payment(authority, amount_rial)
    
    def _mock_request_payment(self, amount_rial: int, description: str, callback_url: str) -> Dict[str, str]:
        """Mock payment request for testing"""
        authority = f"A-MOCK-{uuid.uuid4().hex[:16]}"
        redirect_url = f"{self.base_url}/redirect/{authority}"
        
        return {
            "authority": authority,
            "url": redirect_url
        }
    
    def _mock_verify_payment(self, authority: str, amount_rial: int) -> Dict[str, Union[bool, str, int]]:
        """Mock payment verification for testing"""
        # Mock verification logic - in real implementation, this would check the authority format
        if authority.startswith("A-MOCK-") and amount_rial > 0:
            ref_id = f"R-MOCK-{uuid.uuid4().hex[:16]}"
            return {
                "ok": True,
                "ref_id": ref_id,
                "code": 100,
                "message": "Payment verified successfully (mock mode)"
            }
        else:
            return {
                "ok": False,
                "ref_id": None,
                "code": 400,
                "message": "Invalid authority or amount (mock mode)"
            }
    
    async def _real_request_payment(
        self, 
        amount_rial: int, 
        description: str, 
        callback_url: str, 
        email: Optional[str] = None, 
        mobile: Optional[str] = None
    ) -> Dict[str, str]:
        """Real Zarinpal payment request"""
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": amount_rial,
            "Description": description,
            "CallbackURL": callback_url,
            "Metadata": {}
        }
        
        if email:
            payload["Metadata"]["email"] = email
        if mobile:
            payload["Metadata"]["mobile"] = mobile
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/PaymentRequest.json",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("Status") == 100:
                    authority = data.get("Authority")
                    payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
                    
                    return {
                        "authority": authority,
                        "url": payment_url
                    }
                else:
                    error_code = data.get("Status", -1)
                    error_message = data.get("Errors", {}).get("0", "Unknown error")
                    raise Exception(f"Zarinpal error {error_code}: {error_message}")
                    
        except httpx.TimeoutException:
            raise Exception("Request timeout")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Payment request failed: {str(e)}")
    
    async def _real_verify_payment(self, authority: str, amount_rial: int) -> Dict[str, Union[bool, str, int]]:
        """Real Zarinpal payment verification"""
        payload = {
            "MerchantID": self.merchant_id,
            "Authority": authority,
            "Amount": amount_rial
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/PaymentVerification.json",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("Status") == 100:
                    ref_id = data.get("RefID")
                    return {
                        "ok": True,
                        "ref_id": ref_id,
                        "code": data.get("Status"),
                        "message": "Payment verified successfully"
                    }
                else:
                    error_code = data.get("Status", -1)
                    error_message = data.get("Errors", {}).get("0", "Unknown error")
                    return {
                        "ok": False,
                        "ref_id": None,
                        "code": error_code,
                        "message": error_message
                    }
                    
        except httpx.TimeoutException:
            return {
                "ok": False,
                "ref_id": None,
                "code": -1,
                "message": "Request timeout"
            }
        except httpx.HTTPStatusError as e:
            return {
                "ok": False,
                "ref_id": None,
                "code": e.response.status_code,
                "message": f"HTTP error: {e.response.status_code}"
            }
        except Exception as e:
            return {
                "ok": False,
                "ref_id": None,
                "code": -1,
                "message": f"Verification failed: {str(e)}"
            }
