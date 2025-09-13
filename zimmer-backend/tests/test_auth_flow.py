from tests.factories import user_payload, creds
from models.user import User
from utils.security import hash_password

def test_login_me_logout(client, db_session):
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
    
    # Debug: Check if user was created
    print(f"Created user: {test_user.email}, role: {test_user.role}, is_active: {test_user.is_active}")

    # LOGIN
    login_data = creds(up["email"])
    print(f"Login data: {login_data}")
    r = client.post("/api/login", json=login_data)
    print(f"Login response status: {r.status_code}")
    print(f"Login response body: {r.text}")
    assert r.status_code == 200
    login_response = r.json()
    assert "access_token" in login_response
    assert login_response.get("email") == up["email"]

    # ME (using /api/me)
    r = client.get("/api/me", headers={"Authorization": f"Bearer {login_response['access_token']}"})
    print(f"Profile response status: {r.status_code}")
    print(f"Profile response body: {r.text}")
    assert r.status_code == 200
    me = r.json()
    assert me.get("email") == up["email"]

    # LOGOUT
    r = client.post("/api/logout")
    assert r.status_code in (200, 204)
