import json
from tests.factories import user_payload, creds
from models.user import User
from models.automation import Automation, PricingType
from utils.security import hash_password

def _auth_headers(client, email):
    r = client.post("/api/auth/login", json=creds(email))
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_payment_init_verify_mocked(client, db_session, monkeypatch):
    # Create a test user directly in the database
    up = user_payload()
    test_user = User(
        name=up["name"],
        email=up["email"],
        password_hash=hash_password(up["password"]),
        role=up["role"],
        is_active=True
    )
    db_session.add(test_user)
    
    # Create a test automation with required health_status field
    test_automation = Automation(
        name="Test Automation",
        description="Test automation for payments",
        pricing_type=PricingType.token_per_session,
        price_per_token=10.0,
        status=True,
        api_endpoint="/test",
        health_status="healthy",  # Must be healthy for purchase
        is_listed=True  # Must be listed for purchase
    )
    db_session.add(test_automation)
    db_session.commit()
    db_session.refresh(test_user)
    db_session.refresh(test_automation)

    headers = _auth_headers(client, up["email"])

    # Mock external call(s) your payment router makes
    # Adjust import path and function names to match your code.
    # Example if your code calls a function like app.services.zarinpal.create_payment(...)
    try:
        from utils import zarinpal as z
    except Exception:
        z = None

    if z:
        def fake_create_payment(amount:int, **kwargs):
            return {"authority": "TEST_AUTH", "url": "https://sandbox.zarinpal.com/start/TEST_AUTH"}
        def fake_verify_payment(authority:str, **kwargs):
            return {"status":"OK", "ref_id":"REF123"}
        monkeypatch.setattr(z, "create_payment", fake_create_payment, raising=False)
        monkeypatch.setattr(z, "verify_payment", fake_verify_payment, raising=False)

    # INIT
    payload = {"automation_id": test_automation.id, "tokens": 10, "return_path": "https://example.com/callback"}
    r = client.post("/api/payments/zarinpal/init", headers=headers, json=payload)
    print(f"Payment init response status: {r.status_code}")
    print(f"Payment init response body: {r.text}")
    assert r.status_code in (200, 201)
    init_js = r.json()
    assert "status" in init_js or "authority" in json.dumps(init_js)

    # VERIFY (simulate callback path)
    # The verify endpoint is actually a GET callback with query parameters
    vr = client.get(f"/api/payments/zarinpal/callback?payment_id={init_js['payment_id']}&Authority={init_js['authority']}&Status=OK")
    print(f"Payment verify response status: {vr.status_code}")
    print(f"Payment verify response body: {vr.text}")
    # Some backends return 200 or 204; accept both
    assert vr.status_code in (200, 204, 201)
