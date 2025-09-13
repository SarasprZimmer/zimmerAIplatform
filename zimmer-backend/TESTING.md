# Zimmer Backend Testing Guide

## Overview

This document provides a comprehensive guide for testing the Zimmer backend application. The test suite uses pytest and includes unit tests, integration tests, and API contract tests.

## Test Structure

```
tests/
├── __init__.py              # Makes tests a Python package
├── conftest.py              # Pytest fixtures and configuration
├── factories.py             # Test data factories using Faker
├── test_health.py           # Health check endpoint tests
├── test_auth_flow.py        # Authentication flow tests
├── test_notifications.py    # Notification system tests
├── test_payments_sandbox.py # Payment system tests (mocked)
├── test_admin_notifications.py # Admin notification tests
└── test_migrations_guard.py # Migration safety tests
```

## Setup

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Environment Configuration

The tests use a SQLite test database by default. You can override this with:

```bash
export TEST_DATABASE_URL=sqlite:///./test.db
```

### 3. Database Setup

Tests automatically create and tear down a fresh test database for each test session. No manual setup required.

## Running Tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_auth_flow.py -v
```

### Run Specific Test Function

```bash
python -m pytest tests/test_auth_flow.py::test_login_me_logout -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=app --cov-report=html
```

### Run with Debug Output

```bash
python -m pytest tests/ -v -s
```

## Test Categories

### 1. Health Check Tests (`test_health.py`)

Tests the basic health endpoint to ensure the application is running.

```python
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    assert js.get("status") is not None
```

### 2. Authentication Flow Tests (`test_auth_flow.py`)

Tests the complete user authentication flow:
- User creation in database
- Login with credentials
- Profile retrieval
- Logout

```python
def test_login_me_logout(client, db_session):
    # Create test user directly in database
    # Login and get access token
    # Retrieve user profile
    # Logout
```

### 3. Notification System Tests (`test_notifications.py`)

Tests user-facing notification endpoints:
- List notifications
- Mark notifications as read
- Mark all notifications as read

### 4. Admin Notification Tests (`test_admin_notifications.py`)

Tests admin notification creation and broadcasting:
- Create notifications for specific users
- Broadcast notifications to all users
- Verify notifications are received

### 5. Payment System Tests (`test_payments_sandbox.py`)

Tests the payment initialization and verification flow:
- Payment initialization with automation
- Payment verification via callback
- Mocked external payment gateway calls

### 6. Migration Safety Tests (`test_migrations_guard.py`)

Ensures that `Base.metadata.create_all()` is not called on application startup, relying on Alembic for migrations.

## Test Fixtures

### Database Fixtures

- `db_engine`: Creates a test database engine
- `db_session`: Provides a database session for each test
- `client`: FastAPI TestClient with database overrides

### Authentication Fixtures

- `user_payload()`: Generates fake user data
- `creds(email)`: Generates login credentials

## Database Overrides

The test configuration overrides all `get_db` dependencies to use the test database:

```python
# Override all get_db functions to use test database
app.dependency_overrides[get_db] = _get_db
app.dependency_overrides[users_get_db] = _get_db
app.dependency_overrides[auth_get_db] = _get_db
# ... and more
```

## Mocking External Services

### Payment Gateway Mocking

Payment tests mock external Zarinpal API calls:

```python
def fake_create_payment(amount:int, **kwargs):
    return {"authority": "TEST_AUTH", "url": "https://sandbox.zarinpal.com/start/TEST_AUTH"}

def fake_verify_payment(authority:str, **kwargs):
    return {"status":"OK", "ref_id":"REF123"}

monkeypatch.setattr(z, "create_payment", fake_create_payment, raising=False)
monkeypatch.setattr(z, "verify_payment", fake_verify_payment, raising=False)
```

## Test Data Management

### Using Factories

Test data is generated using Faker factories:

```python
from tests.factories import user_payload, creds

# Generate fake user data
up = user_payload()  # Returns dict with name, email, password, role

# Generate login credentials
login_data = creds(up["email"])  # Returns dict with email and password
```

### Direct Database Creation

For tests that need specific data, users and other entities are created directly in the database:

```python
test_user = User(
    name=up["name"],
    email=up["email"],
    password_hash=hash_password(up["password"]),
    role=up["role"],
    is_active=True
)
db_session.add(test_user)
db_session.commit()
```

## JWT Token Handling

The tests handle both legacy and new JWT token formats:

- Legacy format: Nested user object
- New format: Standard JWT claims with `sub` field

The `get_user_id_from_access_token` function supports both formats for backward compatibility.

## Best Practices

### 1. Test Isolation

Each test runs in isolation with a fresh database session. No test should depend on another test's state.

### 2. Clean Setup/Teardown

Tests create their own test data and clean up automatically via pytest fixtures.

### 3. Meaningful Assertions

Tests include specific assertions that verify the expected behavior:

```python
assert r.status_code == 200
assert "access_token" in login_response
assert login_response.get("email") == up["email"]
```

### 4. Debug Output

Tests include debug output for troubleshooting:

```python
print(f"Login response status: {r.status_code}")
print(f"Login response body: {r.text}")
```

### 5. Error Handling

Tests verify both success and error conditions where appropriate.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all required packages are installed
2. **Database Errors**: Check that the test database URL is correct
3. **JWT Token Issues**: Verify token format compatibility
4. **404 Errors**: Check endpoint paths and HTTP methods

### Debug Mode

Run tests with `-s` flag to see print statements:

```bash
python -m pytest tests/ -v -s
```

### Verbose Output

Use `-v` flag for detailed test output:

```bash
python -m pytest tests/ -v
```

## Continuous Integration

The test suite is designed to run in CI environments:

- Uses SQLite for fast execution
- No external dependencies (mocked)
- Clean setup/teardown
- Deterministic results

## Coverage Goals

- API endpoints: 100%
- Core business logic: 90%+
- Error handling: 80%+
- Integration flows: 100%

## Future Enhancements

1. **Performance Tests**: Add load testing for critical endpoints
2. **Security Tests**: Add tests for authentication bypass scenarios
3. **API Contract Tests**: Add OpenAPI schema validation tests
4. **Database Migration Tests**: Add tests for migration rollbacks
5. **Integration Tests**: Add tests with real external services (optional)
