import datetime as dt
from fastapi.testclient import TestClient
from database import SessionLocal
from main import app
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from models.payment import Payment

def seed(db):
    u = db.query(User).first()
    if not u:
        u = User(name="U", email="u@example.com", password_hash="x", is_active=True)
        db.add(u); db.commit(); db.refresh(u)
    a = db.query(Automation).first()
    if not a:
        a = Automation(name="Auto A", description="...", pricing_type="token_per_step", price_per_token=1.0, status=True, api_endpoint="/x", service_token_hash="h")
        db.add(a); db.commit(); db.refresh(a)
    ua = db.query(UserAutomation).filter_by(user_id=u.id, automation_id=a.id).first()
    if not ua:
        ua = UserAutomation(user_id=u.id, automation_id=a.id, tokens_remaining=120, demo_tokens=5, is_demo_active=True, status="active", integration_status="ok")
        db.add(ua); db.commit()
    p = Payment(user_id=u.id, automation_id=a.id, amount=100000, tokens_purchased=100, gateway="zarinpal", method="online", status="success", transaction_id="tx1", ref_id="r1", created_at=dt.datetime.utcnow())
    db.add(p); db.commit()
    return u, a

def test_billing_smoke():
    client = TestClient(app)
    db = SessionLocal()
    u, a = seed(db)

    r1 = client.get("/api/user/automations/active")
    assert r1.status_code in (200, 401)

    r2 = client.get("/api/user/payments")
    assert r2.status_code in (200, 401)

    r3 = client.get("/api/user/payments/summary")
    assert r3.status_code in (200, 401)
