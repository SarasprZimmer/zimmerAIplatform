from tests.factories import user_payload, creds
from models.user import User
from utils.security import hash_password

def _login(client, email):
    r = client.post("/api/login", json=creds(email))
    assert r.status_code == 200
    return r.json()["access_token"]

def test_notifications_list_and_mark(client, db_session):
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
    db_session.commit()
    db_session.refresh(test_user)

    token = _login(client, up["email"])

    # list empty
    r = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)

    # If you have a service to create a noti via API/admin, you can call it here.
    # Otherwise this is a contract test proving the endpoints are reachable.

    # mark-all should not fail on empty
    r = client.post("/api/notifications/mark-all-read", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (200, 201, 204)
