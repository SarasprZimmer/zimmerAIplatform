import datetime as dt
from fastapi.testclient import TestClient
from database import SessionLocal, engine
from models.user import User
from models.token_usage import TokenUsage
from main import app

def auth_headers(client: TestClient):
    # Replace with your real auth helper if present
    # Here we assume there's a seeded user or a test login fixture.
    # For now, bypass if your test setup already injects a session/cookie.
    return {}

def seed_usage(db, user_id, automation_id, tokens, days_ago):
    db.add(TokenUsage(
        user_id=user_id,
        automation_id=automation_id,
        tokens_used=tokens,
        created_at=dt.datetime.utcnow() - dt.timedelta(days=days_ago),
    ))

def test_usage_endpoints_smoke(monkeypatch):
    client = TestClient(app)
    db = SessionLocal()
    # NOTE: Adjust user creation to your factories if needed
    u = db.query(User).first()
    if not u:
        u = User(name="Test", email="u@example.com", password_hash="x", is_active=True)
        db.add(u); db.commit(); db.refresh(u)

    # seed a few rows
    seed_usage(db, u.id, 1, 100, 1)
    seed_usage(db, u.id, 1, 50, 2)
    seed_usage(db, u.id, 2, 25, 2)
    db.commit()

    r = client.get("/api/user/usage", params={"range":"7d"})
    assert r.status_code in (200, 401)

    r2 = client.get("/api/user/usage/distribution")
    assert r2.status_code in (200, 401)
