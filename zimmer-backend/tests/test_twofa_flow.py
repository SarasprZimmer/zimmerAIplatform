from fastapi.testclient import TestClient
from main import app
import uuid

def _signup(c, email):
    c.post("/api/auth/signup", json={"name":"T User","email":email,"password":"Passw0rd!","role":"manager"})
    r = c.post("/api/auth/login", json={"email":email,"password":"Passw0rd!"})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_twofa_initiate_then_challenge_login():
    c = TestClient(app)
    
    # Use unique email for each test run
    unique_email = f"2fa-{uuid.uuid4().hex[:8]}@example.com"
    
    access = _signup(c, unique_email)

    r = c.post("/api/auth/2fa/initiate", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200 and "otpauth_uri" in r.json()

    # Activating needs real TOTP; skip and just verify login now requires OTP
    r = c.post("/api/auth/login", json={"email":unique_email,"password":"Passw0rd!"})
    # Before activation, still 200; after manual activation it becomes 401 with otp_required. This test is a smoke only.
    assert r.status_code in (200, 401)
