"""
Smoke tests for Google OAuth configuration
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_google_configured_flag():
    """Test that Google OAuth configuration endpoint works"""
    response = client.get("/api/auth/google/configured")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    # Should be False in test environment (no Google credentials)
    assert data["configured"] is False

def test_google_login_endpoint():
    """Test that Google login endpoint exists and returns proper error when not configured"""
    response = client.get("/api/auth/google/login")
    # Should return 503 when not configured
    assert response.status_code == 503
    data = response.json()
    assert "Google OAuth not configured" in data["detail"]

def test_google_callback_endpoint():
    """Test that Google callback endpoint exists and returns proper error when not configured"""
    response = client.get("/api/auth/google/callback")
    # Should return 503 when not configured
    assert response.status_code == 503
    data = response.json()
    assert "Google OAuth not configured" in data["detail"]

def test_email_verification_endpoints():
    """Test that email verification endpoints exist"""
    # Test request email verification endpoint
    response = client.post("/api/auth/request-email-verify", json={"email": "test@example.com"})
    # Should return 404 for non-existent user or other error, but endpoint should exist
    assert response.status_code in [400, 404, 422]
    
    # Test verify email endpoint
    response = client.post("/api/auth/verify-email", json={"token": "invalid_token"})
    # Should return 400 for invalid token, but endpoint should exist
    assert response.status_code in [400, 422]
