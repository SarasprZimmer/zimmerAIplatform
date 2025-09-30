from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import httpx
import asyncio
from urllib.parse import urlparse
import re
from database import get_db
from utils.auth_dependency import get_current_admin_user
from models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class URLValidationResult:
    def __init__(self, url: str, status: str, message: str, details: Optional[Dict] = None):
        self.url = url
        self.status = status  # 'valid', 'invalid', 'error'
        self.message = message
        self.details = details or {}

@router.post("/automations/validate-urls")
async def validate_automation_urls(
    urls: Dict[str, str],
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Validate automation URLs and test their accessibility
    """
    try:
        results = {}
        
        # Validate each URL
        for url_type, url in urls.items():
            if not url:
                results[url_type] = URLValidationResult(
                    url=url,
                    status="invalid",
                    message="URL is required"
                ).__dict__
                continue
                
            # Basic URL format validation
            if not is_valid_url(url):
                results[url_type] = URLValidationResult(
                    url=url,
                    status="invalid",
                    message="Invalid URL format"
                ).__dict__
                continue
            
            # Test URL accessibility
            test_result = await test_url_accessibility(url, url_type)
            results[url_type] = test_result.__dict__
        
        # Overall validation status
        all_valid = all(result["status"] == "valid" for result in results.values())
        
        return {
            "overall_status": "valid" if all_valid else "invalid",
            "can_generate_token": all_valid,
            "results": results,
            "summary": generate_validation_summary(results)
        }
        
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"URL validation failed: {str(e)}"
        )

@router.post("/automations/{automation_id}/generate-service-token")
async def generate_service_token(
    automation_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Generate a service token for an automation
    """
    try:
        from models.automation import Automation
        import secrets
        import hashlib
        
        # Get automation
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        # Generate service token
        service_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(service_token.encode()).hexdigest()
        
        # Update automation with token hash
        automation.service_token_hash = token_hash
        db.commit()
        
        # Return token (only shown once)
        return {
            "success": True,
            "service_token": service_token,
            "automation_id": automation_id,
            "message": "Service token generated successfully",
            "instructions": generate_token_instructions(service_token, automation_id)
        }
        
    except Exception as e:
        logger.error(f"Service token generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Service token generation failed: {str(e)}"
        )

def is_valid_url(url: str) -> bool:
    """Check if URL has valid format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

async def test_url_accessibility(url: str, url_type: str) -> URLValidationResult:
    """Test if URL is accessible and properly structured"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with GET request first
            response = await client.get(url)
            
            # Check response status
            if response.status_code in [200, 404, 405]:
                # 404/405 are acceptable for POST-only endpoints
                if url_type in ["provision", "usage", "kb_reset"] and response.status_code == 405:
                    return URLValidationResult(
                        url=url,
                        status="valid",
                        message="Endpoint accessible (POST-only endpoint)",
                        details={
                            "status_code": response.status_code,
                            "method_allowed": "POST",
                            "content_type": response.headers.get("content-type", "unknown")
                        }
                    )
                elif response.status_code == 200:
                    return URLValidationResult(
                        url=url,
                        status="valid",
                        message="Endpoint accessible",
                        details={
                            "status_code": response.status_code,
                            "content_type": response.headers.get("content-type", "unknown"),
                            "response_size": len(response.content)
                        }
                    )
                else:
                    return URLValidationResult(
                        url=url,
                        status="invalid",
                        message=f"Unexpected status code: {response.status_code}",
                        details={"status_code": response.status_code}
                    )
            else:
                return URLValidationResult(
                    url=url,
                    status="error",
                    message=f"HTTP {response.status_code}: {response.reason_phrase}",
                    details={"status_code": response.status_code}
                )
                
    except httpx.TimeoutException:
        return URLValidationResult(
            url=url,
            status="error",
            message="Request timeout - URL may be unreachable",
            details={"error_type": "timeout"}
        )
    except httpx.ConnectError:
        return URLValidationResult(
            url=url,
            status="error",
            message="Connection failed - URL may be invalid or server down",
            details={"error_type": "connection_error"}
        )
    except Exception as e:
        return URLValidationResult(
            url=url,
            status="error",
            message=f"Unexpected error: {str(e)}",
            details={"error_type": "unexpected", "error": str(e)}
        )

def generate_validation_summary(results: Dict) -> str:
    """Generate a summary of validation results"""
    valid_count = sum(1 for result in results.values() if result["status"] == "valid")
    total_count = len(results)
    
    if valid_count == total_count:
        return f"✅ All {total_count} URLs are valid and accessible"
    elif valid_count == 0:
        return f"❌ None of the {total_count} URLs are accessible"
    else:
        return f"⚠️ {valid_count} of {total_count} URLs are valid"

def generate_token_instructions(service_token: str, automation_id: int) -> Dict:
    """Generate instructions for automation developers"""
    return {
        "integration_steps": [
            "1. Add the service token to your automation's environment variables",
            "2. Verify the X-Zimmer-Service-Token header in incoming requests",
            "3. Only process requests with valid tokens",
            "4. Return appropriate error responses for invalid tokens"
        ],
        "code_example": f"""
# Example Python code for token validation
import os
from fastapi import HTTPException, Header

SERVICE_TOKEN = "{service_token}"

async def verify_zimmer_token(x_zimmer_service_token: str = Header(None)):
    if not x_zimmer_service_token:
        raise HTTPException(status_code=401, detail="Missing service token")
    
    if x_zimmer_service_token != SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid service token")
    
    return True

# Use in your endpoints
@app.post("/provision")
async def provision_endpoint(
    request_data: dict,
    token_valid: bool = Depends(verify_zimmer_token)
):
    # Your automation logic here
    return {{"success": True}}
        """,
        "environment_variable": f"AUTOMATION_{automation_id}_SERVICE_TOKEN={service_token}",
        "security_notes": [
            "Keep the service token secure and never expose it in logs",
            "The token is unique to this automation",
            "Store it as an environment variable, not in code",
            "Rotate the token if it's ever compromised"
        ]
    }
