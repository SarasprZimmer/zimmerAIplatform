#!/usr/bin/env python3
"""
Admin Endpoints Test Script
Tests all the newly implemented admin endpoints
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
BASE_URL = "https://api.zimmerai.com"
TEST_USER_EMAIL = "admin_test@example.com"
TEST_USER_PASSWORD = "AdminTest123!"

def make_request(method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
    """Make HTTP request and measure response time"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response_time = time.time() - start_time
        
        return {
            "status_code": response.status_code,
            "response_time": response_time,
            "headers": dict(response.headers),
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "status_code": 0,
            "response_time": response_time,
            "error": str(e)
        }

def get_auth_token():
    """Get authentication token for testing"""
    # Try to create user first
    signup_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "name": "Admin Test User",
        "confirm_password": TEST_USER_PASSWORD
    }
    
    signup_result = make_request("POST", "/api/auth/signup", signup_data)
    
    if signup_result["status_code"] == 201:
        return signup_result["data"].get("access_token")
    elif signup_result["status_code"] in [400, 409]:
        # User exists, try login
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        login_result = make_request("POST", "/api/auth/login", login_data)
        if login_result["status_code"] == 200:
            return login_result["data"].get("access_token")
    
    return None

def log_test(test_name: str, status: str, details: str, response_time: float = 0.0):
    """Log test result"""
    status_icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠", "SKIP": "-"}
    icon = status_icon.get(status, "?")
    print(f"{icon} {test_name}: {details} ({response_time:.3f}s)")

def test_admin_endpoints():
    """Test all admin endpoints"""
    print("Admin Endpoints Testing for Zimmer AI Platform")
    print("=" * 60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints
    test_cases = [
        # Token Management
        {
            "name": "Token Management - Adjust",
            "method": "POST",
            "endpoint": "/api/admin/tokens/adjust",
            "data": {"user_id": 1, "tokens": 10, "reason": "Test adjustment"},
            "expected_status": [403, 401]  # Should deny access to regular user
        },
        {
            "name": "Token Management - History",
            "method": "GET",
            "endpoint": "/api/admin/tokens/history",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "Token Management - User Tokens",
            "method": "GET",
            "endpoint": "/api/admin/user-tokens",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "Token Management - Stats",
            "method": "GET",
            "endpoint": "/api/admin/tokens/stats",
            "data": None,
            "expected_status": [403, 401]
        },
        
        # Usage Statistics
        {
            "name": "Usage Stats - System Stats",
            "method": "GET",
            "endpoint": "/api/admin/usage/stats",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "Usage Stats - User Usage",
            "method": "GET",
            "endpoint": "/api/admin/usage/1",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "Usage Stats - Automation Usage",
            "method": "GET",
            "endpoint": "/api/admin/usage/automation/1",
            "data": None,
            "expected_status": [403, 401]
        },
        
        # System Monitoring
        {
            "name": "System Monitoring - Status",
            "method": "GET",
            "endpoint": "/api/admin/system/status",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "System Monitoring - Dashboard Stats",
            "method": "GET",
            "endpoint": "/api/admin/dashboard/stats",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "System Monitoring - Health Check",
            "method": "GET",
            "endpoint": "/api/admin/system/health",
            "data": None,
            "expected_status": [403, 401]
        },
        
        # KB Extended
        {
            "name": "KB Extended - Templates",
            "method": "GET",
            "endpoint": "/api/admin/kb-templates",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "KB Extended - Status",
            "method": "GET",
            "endpoint": "/api/admin/kb-status?automation_id=1",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "KB Extended - Monitoring",
            "method": "GET",
            "endpoint": "/api/admin/kb-monitoring",
            "data": None,
            "expected_status": [403, 401]
        },
        
        # Backup Management (using existing endpoints)
        {
            "name": "Backup Management - List Backups",
            "method": "GET",
            "endpoint": "/api/admin/backups",
            "data": None,
            "expected_status": [403, 401]
        },
        {
            "name": "Backup Management - Trigger Backup",
            "method": "POST",
            "endpoint": "/api/admin/backups/trigger",
            "data": {"backup_type": "full"},
            "expected_status": [403, 401]
        },
        {
            "name": "Backup Management - Backup Stats",
            "method": "GET",
            "endpoint": "/api/admin/backups/stats",
            "data": None,
            "expected_status": [403, 401]
        },
        
        # Notification Management (using existing endpoints)
        {
            "name": "Notification Management - Create Notification",
            "method": "POST",
            "endpoint": "/api/admin/notifications",
            "data": {
                "type": "system",
                "title": "Test notification",
                "body": "This is a test notification"
            },
            "expected_status": [403, 401]
        },
        {
            "name": "Notification Management - Broadcast",
            "method": "POST",
            "endpoint": "/api/admin/notifications/broadcast",
            "data": {
                "type": "system",
                "title": "Test broadcast",
                "body": "This is a test broadcast"
            },
            "expected_status": [403, 401]
        }
    ]
    
    passed = 0
    failed = 0
    warnings = 0
    
    for test_case in test_cases:
        if test_case["method"] == "GET":
            result = make_request("GET", test_case["endpoint"], headers=headers)
        else:
            result = make_request(test_case["method"], test_case["endpoint"], 
                                test_case["data"], headers)
        
        if result["status_code"] in test_case["expected_status"]:
            log_test(test_case["name"], "PASS", 
                    f"Properly denied access (got {result['status_code']})", 
                    result["response_time"])
            passed += 1
        elif result["status_code"] == 404:
            log_test(test_case["name"], "WARN", 
                    "Endpoint not found (404)", result["response_time"])
            warnings += 1
        else:
            log_test(test_case["name"], "FAIL", 
                    f"Unexpected response: {result['status_code']}", 
                    result["response_time"])
            failed += 1
    
    # Summary
    total = passed + failed + warnings
    print("\n" + "=" * 60)
    print("ADMIN ENDPOINTS TEST REPORT")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Warnings: {warnings}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if warnings > 0:
        print(f"\n⚠️  {warnings} endpoints still returning 404 (not implemented)")
    
    if failed > 0:
        print(f"\n❌ {failed} endpoints have unexpected behavior")
    
    if passed == total:
        print("\n✅ All admin endpoints are properly secured!")
    elif passed + warnings == total:
        print("\n✅ All implemented endpoints are properly secured!")
    
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "success_rate": (passed/total)*100
    }

if __name__ == "__main__":
    test_admin_endpoints()
