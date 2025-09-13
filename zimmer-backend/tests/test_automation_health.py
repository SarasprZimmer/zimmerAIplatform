import pytest
from tests.factories import user_payload, creds
from models.user import User
from models.automation import Automation, PricingType
from utils.security import hash_password

def _mk_admin(client, db_session):
    """Create an admin user and return their token"""
    import uuid
    unique_email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    up = user_payload(email=unique_email, role="manager")
    admin_user = User(
        name=up["name"],
        email=up["email"],
        password_hash=hash_password(up["password"]),
        role=up["role"],
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    r = client.post("/api/login", json=creds(up["email"]))
    assert r.status_code == 200
    return r.json()["access_token"]

def _create_automation(db_session, health_check_url=None):
    """Create a test automation"""
    automation = Automation(
        name="Test Automation",
        description="Test automation for health checks",
        pricing_type=PricingType.token_per_session,
        price_per_token=10.0,
        status=True,
        api_endpoint="/test",
        health_check_url=health_check_url
    )
    db_session.add(automation)
    db_session.commit()
    db_session.refresh(automation)
    return automation

@pytest.mark.asyncio
async def test_health_check_blocking(client, db_session, monkeypatch):
    """Test that health checks block unhealthy automations from being listed"""
    admin_token = _mk_admin(client, db_session)
    
    # Mock the probe function
    from services import automation_health as H
    
    # First, create automation with healthy probe
    async def fake_probe_healthy(url: str):
        return {"ok": True, "body": {"status":"ok","version":"1.0.0","uptime":123}}
    
    monkeypatch.setattr(H, "probe", fake_probe_healthy)
    
    # Create automation with health check URL
    automation_data = {
        "name": "Healthy Automation",
        "description": "Test automation",
        "pricing_type": "token_per_session",
        "price_per_token": 10.0,
        "status": True,
        "health_check_url": "https://example.com/health"
    }
    
    r = client.post("/api/admin/automations", 
                   headers={"Authorization": f"Bearer {admin_token}"},
                   json=automation_data)
    assert r.status_code == 200
    
    automation = r.json()
    assert automation["health_status"] == "healthy"
    assert automation["is_listed"] is True
    
    # Now test purchase gate - should work for healthy automation
    user_up = user_payload(email="user@example.com", role="support_staff")
    user = User(
        name=user_up["name"],
        email=user_up["email"],
        password_hash=hash_password(user_up["password"]),
        role=user_up["role"],
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    user_token = client.post("/api/login", json=creds(user_up["email"])).json()["access_token"]
    
    # Try to purchase from healthy automation
    payment_data = {
        "automation_id": automation["id"],
        "tokens": 10,
        "return_path": "https://example.com/callback"
    }
    
    r = client.post("/api/payments/zarinpal/init",
                   headers={"Authorization": f"Bearer {user_token}"},
                   json=payment_data)
    assert r.status_code == 200
    
    # Now flip to unhealthy
    async def fake_probe_unhealthy(url: str):
        return {"ok": False, "error": "http_500"}
    
    monkeypatch.setattr(H, "probe", fake_probe_unhealthy)
    
    # Manual trigger should mark it unhealthy and unlist
    r = client.post(f"/api/admin/automations/{automation['id']}/health-check",
                   headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    result = r.json()
    assert result["health_status"] == "unhealthy"
    assert result["is_listed"] is False
    
    # Try to purchase from unhealthy automation - should fail
    r = client.post("/api/payments/zarinpal/init",
                   headers={"Authorization": f"Bearer {user_token}"},
                   json=payment_data)
    assert r.status_code == 400
    assert "unavailable" in r.json()["detail"]

def test_public_listing_filter(client, db_session, monkeypatch):
    """Test that public listing only shows healthy automations"""
    admin_token = _mk_admin(client, db_session)
    
    # Create two automations - one healthy, one unhealthy
    healthy_automation = _create_automation(db_session, "https://healthy.com/health")
    unhealthy_automation = _create_automation(db_session, "https://unhealthy.com/health")
    
    # Mock probe to return different results
    async def fake_probe(url: str):
        if "https://healthy.com" in url:
            return {"ok": True, "body": {"status":"ok","version":"1.0.0","uptime":123}}
        else:
            return {"ok": False, "error": "http_500"}
    
    # Patch the probe function in both places
    from services import automation_health as H
    monkeypatch.setattr(H, "probe", fake_probe)
    
    # Also patch in the admin automation health router
    from routers import admin_automation_health
    monkeypatch.setattr(admin_automation_health, "probe", fake_probe)
    
    # Run health checks
    r = client.post(f"/api/admin/automations/{healthy_automation.id}/health-check",
                   headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert r.json()["health_status"] == "healthy"
    
    r = client.post(f"/api/admin/automations/{unhealthy_automation.id}/health-check",
                   headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert r.json()["health_status"] == "unhealthy"
    
    # Create a regular user
    user_up = user_payload(email="user@example.com", role="support_staff")
    user = User(
        name=user_up["name"],
        email=user_up["email"],
        password_hash=hash_password(user_up["password"]),
        role=user_up["role"],
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    user_token = client.post("/api/login", json=creds(user_up["email"])).json()["access_token"]
    
    # Check public listing - should only show healthy automation
    r = client.get("/api/automations/available",
                  headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 200
    
    automations = r.json()
    assert len(automations) == 1
    assert automations[0]["id"] == healthy_automation.id

def test_automation_creation_with_health_check(client, db_session, monkeypatch):
    """Test that automation creation includes health check"""
    admin_token = _mk_admin(client, db_session)
    
    # Mock probe
    async def fake_probe(url: str):
        return {"ok": True, "body": {"status":"ok","version":"1.0.0","uptime":123}}
    
    # Patch the probe function in both places
    from services import automation_health as H
    monkeypatch.setattr(H, "probe", fake_probe)
    
    # Also patch in the admin automation router (for create endpoint)
    from routers.admin import automation as admin_automation
    monkeypatch.setattr(admin_automation, "probe", fake_probe)
    
    # Create automation with health check URL
    automation_data = {
        "name": "Test Automation",
        "description": "Test automation",
        "pricing_type": "token_per_session",
        "price_per_token": 10.0,
        "status": True,
        "health_check_url": "https://example.com/health"
    }
    
    r = client.post("/api/admin/automations",
                   headers={"Authorization": f"Bearer {admin_token}"},
                   json=automation_data)
    assert r.status_code == 200
    
    automation = r.json()
    assert automation["health_status"] == "healthy"
    assert automation["is_listed"] is True
    assert automation["health_check_url"] == "https://example.com/health"
    assert automation["last_health_at"] is not None

def test_automation_creation_without_health_check(client, db_session):
    """Test that automation creation without health check URL sets appropriate defaults"""
    admin_token = _mk_admin(client, db_session)
    
    # Create automation without health check URL
    automation_data = {
        "name": "Test Automation",
        "description": "Test automation",
        "pricing_type": "token_per_session",
        "price_per_token": 10.0,
        "status": True
    }
    
    r = client.post("/api/admin/automations",
                   headers={"Authorization": f"Bearer {admin_token}"},
                   json=automation_data)
    assert r.status_code == 200
    
    automation = r.json()
    assert automation["health_status"] == "unknown"
    assert automation["is_listed"] is False
    assert automation["health_check_url"] is None

def test_health_check_endpoint(client, db_session, monkeypatch):
    """Test the manual health check endpoint"""
    admin_token = _mk_admin(client, db_session)
    automation = _create_automation(db_session, "https://example.com/health")
    
    # Mock probe
    async def fake_probe(url: str):
        return {"ok": True, "body": {"status":"ok","version":"1.0.0","uptime":123}}
    
    # Patch the probe function in both places
    from services import automation_health as H
    monkeypatch.setattr(H, "probe", fake_probe)
    
    # Also patch in the admin automation health router
    from routers import admin_automation_health
    monkeypatch.setattr(admin_automation_health, "probe", fake_probe)
    
    # Run health check
    r = client.post(f"/api/admin/automations/{automation.id}/health-check",
                   headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    
    result = r.json()
    assert result["automation_id"] == automation.id
    assert result["health_status"] == "healthy"
    assert result["is_listed"] is True
    assert result["last_health_at"] is not None
    assert result["details"]["ok"] is True

def test_health_check_with_invalid_url(client, db_session, monkeypatch):
    """Test health check with invalid URL"""
    admin_token = _mk_admin(client, db_session)
    automation = _create_automation(db_session, "https://invalid-url-that-does-not-exist.com/health")
    
    # Mock probe to simulate network error
    async def fake_probe(url: str):
        return {"ok": False, "error": "exception", "detail": "Connection failed"}
    
    # Patch the probe function in both places
    from services import automation_health as H
    monkeypatch.setattr(H, "probe", fake_probe)
    
    # Also patch in the admin automation health router
    from routers import admin_automation_health
    monkeypatch.setattr(admin_automation_health, "probe", fake_probe)
    
    # Run health check
    r = client.post(f"/api/admin/automations/{automation.id}/health-check",
                   headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    
    result = r.json()
    assert result["health_status"] == "unhealthy"
    assert result["is_listed"] is False
    assert result["details"]["ok"] is False
