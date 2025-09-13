from fastapi.testclient import TestClient
from main import app
from database import get_db
from sqlalchemy.orm import Session

def create_admin_discount(db: Session, code="WELCOME", percent=20, automation_id=None):
    from models.discount import DiscountCode, DiscountCodeAutomation
    dc = DiscountCode(code=code, percent_off=percent, active=True)
    db.add(dc); db.commit(); db.refresh(dc)
    if automation_id:
        db.add(DiscountCodeAutomation(discount_id=dc.id, automation_id=automation_id)); db.commit()
    return dc

def test_validate_and_free_payment(monkeypatch):
    c = TestClient(app)
    # create user
    c.post("/api/auth/register", json={"name":"U","email":"u@example.com","password":"Passw0rd!","role":"manager"})
    r = c.post("/api/auth/login", json={"email":"u@example.com","password":"Passw0rd!"})
    assert r.status_code == 200
    tok = r.json()["access_token"]

    # direct DB setup: one automation id=1 assumed in test db; if not, skip assertion or create it.
    db = next(get_db())
    create_admin_discount(db, code="FREE100", percent=100, automation_id=None)

    # validate
    v = c.post("/api/discounts/validate", json={"code":"FREE100","automation_id":1,"amount":10000}, headers={"Authorization":f"Bearer {tok}"})
    assert v.status_code == 200 and v.json()["valid"] is True and v.json()["amount_after"] == 0

    # init payment with discount_code should auto-complete (amount 0)
    init = c.post("/api/payments/zarinpal/init", json={"automation_id":1,"tokens":10,"discount_code":"FREE100"},
                  headers={"Authorization":f"Bearer {tok}"})
    assert init.status_code == 200
    j = init.json()
    assert j.get("amount")==0
