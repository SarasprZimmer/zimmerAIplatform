import os
import pytest
from tests.factories import user_payload, creds
from models.user import User
from utils.security import hash_password

def _login(client, email):
    r = client.post("/api/login", json=creds(email))
    print(f"Login response status: {r.status_code}")
    print(f"Login response body: {r.text}")
    assert r.status_code == 200
    return r.json()["access_token"]

@pytest.mark.parametrize("admin_email", ["admin@test.com"])
def test_admin_create_and_user_receives(client, db_session, admin_email):
    # Create admin user directly in the database
    admin_user = User(
        name="Admin User",
        email=admin_email,
        password_hash=hash_password("Passw0rd!"),
        role="manager",
        is_active=True
    )
    db_session.add(admin_user)
    
    # Create regular user directly in the database
    regular_user = User(
        name="Regular User",
        email="user1@test.com",
        password_hash=hash_password("Passw0rd!"),
        role="support_staff",
        is_active=True
    )
    db_session.add(regular_user)
    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(regular_user)
    
    admin_token = _login(client, admin_email)

    # create notification for user1
    payload = {
        "user_ids": [regular_user.id],
        "type": "system",
        "title": "Internal Notice",
        "body": "This is a test"
    }
    r = client.post("/api/admin/notifications", headers={"Authorization": f"Bearer {admin_token}"}, json=payload)
    assert r.status_code in (200, 201)
    assert r.json()["created"] == 1

    # login as user1 and read list
    user_token = _login(client, "user1@test.com")
    r = client.get("/api/notifications", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 200
    items = r.json()
    assert any(n["title"] == "Internal Notice" for n in items)
