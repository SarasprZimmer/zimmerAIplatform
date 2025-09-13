import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from .automation_usage import router
from ..schemas.automation import UsageConsumeRequest
from fastapi import FastAPI

# zimmer-backend/routers/test_automation_usage.py



app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def usage_payload():
    return {
        "user_automation_id": 1,
        "units": 5,
        "usage_type": "test",
        "meta": {"foo": "bar"}
    }

def mock_db(user_automation=None, automation=None):
    db = MagicMock()
    db.query().filter().first.side_effect = [user_automation, automation]
    db.refresh = MagicMock()
    return db

def test_no_service_token(client, usage_payload):
    response = client.post("/automation-usage/consume", json=usage_payload)
    assert response.status_code == 401
    assert "توکن سرویس نامعتبر" in response.json()["detail"]

@patch(".automation_usage.get_db", autospec=True)
def test_user_automation_not_found(mock_get_db, client, usage_payload):
    db = mock_db(user_automation=None)
    mock_get_db.return_value = db
    headers = {"X-Zimmer-Service-Token": "token"}
    response = client.post("/automation-usage/consume", json=usage_payload, headers=headers)
    assert response.status_code == 404
    assert "User automation not found" in response.json()["detail"]

@patch(".automation_usage.get_db", autospec=True)
def test_automation_not_found(mock_get_db, client, usage_payload):
    user_automation = MagicMock()
    db = mock_db(user_automation=user_automation, automation=None)
    mock_get_db.return_value = db
    headers = {"X-Zimmer-Service-Token": "token"}
    response = client.post("/automation-usage/consume", json=usage_payload, headers=headers)
    assert response.status_code == 404
    assert "Automation not found" in response.json()["detail"]

@patch(".automation_usage.get_db", autospec=True)
def test_missing_service_token_hash(mock_get_db, client, usage_payload):
    user_automation = MagicMock()
    automation = MagicMock()
    automation.service_token_hash = None
    db = mock_db(user_automation=user_automation, automation=automation)
    mock_get_db.return_value = db
    headers = {"X-Zimmer-Service-Token": "token"}
    response = client.post("/automation-usage/consume", json=usage_payload, headers=headers)
    assert response.status_code == 401
    assert "توکن سرویس نامعتبر" in response.json()["detail"]

@patch(".automation_usage.verify_token", autospec=True)
@patch(".automation_usage.get_db", autospec=True)
def test_invalid_service_token(mock_get_db, mock_verify_token, client, usage_payload):
    user_automation = MagicMock()
    automation = MagicMock()
    automation.service_token_hash = "hash"
    db = mock_db(user_automation=user_automation, automation=automation)
    mock_get_db.return_value = db
    mock_verify_token.return_value = False
    headers = {"X-Zimmer-Service-Token": "token"}
    response = client.post("/automation-usage/consume", json=usage_payload, headers=headers)
    assert response.status_code == 401
    assert "توکن سرویس نامعتبر" in response.json()["detail"]

@patch(".automation_usage.deduct_tokens", autospec=True)
@patch(".automation_usage.verify_token", autospec=True)
@patch(".automation_usage.get_db", autospec=True)
def test_deduct_tokens_failure(mock_get_db, mock_verify_token, mock_deduct_tokens, client, usage_payload):
    user_automation = MagicMock()
    user_automation.demo_tokens = 10
    user_automation.tokens_remaining = 20
    automation = MagicMock()
    automation.service_token_hash = "hash"
    db = mock_db(user_automation=user_automation, automation=automation)
    mock_get_db.return_value = db
    mock_verify_token.return_value = True
    mock_deduct_tokens.return_value = {"success": False, "message": "Not enough tokens"}
    headers = {"X-Zimmer-Service-Token": "token"}
    response = client.post("/automation-usage/consume", json=usage_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is False
    assert data["remaining_demo_tokens"] == 10
    assert data["remaining_paid_tokens"] == 20
    assert data["message"] == "Not enough tokens"

@patch(".automation_usage.deduct_tokens", autospec=True)
@patch(".automation_usage.verify_token", autospec=True)
@patch(".automation_usage.get_db", autospec=True)
def test_deduct_tokens_success(mock_get_db, mock_verify_token, mock_deduct_tokens, client, usage_payload):
    user_automation = MagicMock()
    user_automation.demo_tokens = 8
    user_automation.tokens_remaining = 15
    automation = MagicMock()
    automation.service_token_hash = "hash"
    db = mock_db(user_automation=user_automation, automation=automation)
    mock_get_db.return_value = db
    mock_verify_token.return_value = True
    mock_deduct_tokens.return_value = {"success": True}
    headers = {"X-Zimmer-Service-Token": "token"}
    response = client.post("/automation-usage/consume", json=usage_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is True
    assert data["remaining_demo_tokens"] == 8
    assert data["remaining_paid_tokens"] == 15
    assert data["message"] == "Token consumption successful"