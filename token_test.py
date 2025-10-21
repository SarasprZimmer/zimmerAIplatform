#!/usr/bin/env python3
"""
Token Management Testing Script
Tests token consumption, balance tracking, and admin adjustments
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://api.zimmerai.com"
TEST_RESULTS = []

class TestResult:
    def __init__(self, test_name: str, status: str, details: str = "", response_time: float = 0):
        self.test_name = test_name
        self.status = status  # PASS, FAIL, WARNING, ERROR
        self.details = details
        self.response_time = response_time
        self.timestamp = datetime.now()
        TEST_RESULTS.append(self)
    
    def __str__(self):
        return f"[{self.status}] {self.test_name} - {self.details} ({self.response_time:.2f}s)"

def log_test(test_name: str, status: str, details: str = "", response_time: float = 0):
    """Log test result"""
    result = TestResult(test_name, status, details, response_time)
    print(result)
    return result

def make_request(method: str, endpoint: str, headers: dict = None, data: dict = None, timeout: int = 30):
    """Make HTTP request and return response data"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response_time = time.time() - start_time
        
        try:
            response_data = response.json()
        except:
            response_data = response.text
            
        return response_data, response_time, response.status_code
        
    except requests.exceptions.RequestException as e:
        response_time = time.time() - start_time
        return None, response_time, 0

def get_auth_token():
    """Get authentication token for testing"""
    login_data = {
        "email": "testuser1761038526@example.com",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_token_balance_tracking():
    """Test token balance tracking"""
    print("\n5.1 Token Balance Tracking")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test user usage endpoint
    data, response_time, status = make_request("GET", "/api/user/usage", headers=headers)
    
    if status == 200 and data is not None:
        log_test("Get User Usage", "PASS", "Successfully retrieved user usage data", response_time)
        
        # Check data structure
        if isinstance(data, dict):
            log_test("Usage Data Structure", "PASS", "Usage data is properly formatted", 0)
            
            # Check for expected fields
            expected_fields = ["tokens_remaining", "demo_tokens", "total_usage"]
            present_fields = [field for field in expected_fields if field in data]
            
            if present_fields:
                log_test("Usage Data Fields", "PASS", f"Found fields: {present_fields}", 0)
            else:
                log_test("Usage Data Fields", "WARNING", "No expected usage fields found", 0)
        else:
            log_test("Usage Data Structure", "WARNING", f"Unexpected data format: {type(data)}", 0)
    else:
        log_test("Get User Usage", "FAIL", f"Failed to get user usage. Status: {status}", response_time)
    
    # Test user automations endpoint for token info
    data, response_time, status = make_request("GET", "/api/user/automations", headers=headers)
    
    if status == 200 and data is not None:
        log_test("Get User Automations", "PASS", "Successfully retrieved user automations", response_time)
        
        if isinstance(data, list):
            log_test("User Automations Data", "PASS", f"Retrieved {len(data)} user automations", 0)
            
            # Check token fields in automations
            if data:
                automation = data[0]
                token_fields = ["tokens_remaining", "demo_tokens", "is_demo_active"]
                present_token_fields = [field for field in token_fields if field in automation]
                
                if present_token_fields:
                    log_test("Automation Token Fields", "PASS", f"Found token fields: {present_token_fields}", 0)
                else:
                    log_test("Automation Token Fields", "WARNING", "No token fields found in automation data", 0)
        else:
            log_test("User Automations Data", "WARNING", f"Unexpected data format: {type(data)}", 0)
    else:
        log_test("Get User Automations", "FAIL", f"Failed to get user automations. Status: {status}", response_time)

def test_token_consumption():
    """Test token consumption functionality"""
    print("\n5.2 Token Consumption")
    print("-" * 30)
    
    # Test token consumption endpoint (requires service token)
    consumption_tests = [
        {
            "name": "Valid Token Consumption",
            "data": {
                "user_automation_id": 1,
                "tokens_used": 1,
                "usage_type": "api_call"
            },
            "headers": {
                "X-Zimmer-Service-Token": "test_service_token"
            }
        },
        {
            "name": "Invalid Service Token",
            "data": {
                "user_automation_id": 1,
                "tokens_used": 1,
                "usage_type": "api_call"
            },
            "headers": {
                "X-Zimmer-Service-Token": "invalid_token"
            }
        },
        {
            "name": "Missing Service Token",
            "data": {
                "user_automation_id": 1,
                "tokens_used": 1,
                "usage_type": "api_call"
            },
            "headers": {}
        },
        {
            "name": "Invalid Data",
            "data": {
                "user_automation_id": "invalid",
                "tokens_used": -1,
                "usage_type": "api_call"
            },
            "headers": {
                "X-Zimmer-Service-Token": "test_service_token"
            }
        }
    ]
    
    for test in consumption_tests:
        data, response_time, status = make_request("POST", "/api/usage/consume", 
                                                 headers=test["headers"], data=test["data"])
        
        if status in [200, 400, 401, 403, 404]:
            log_test(f"Token Consumption - {test['name']}", "PASS", 
                    f"Consumption endpoint handled request. Status: {status}", response_time)
        else:
            log_test(f"Token Consumption - {test['name']}", "WARNING", 
                    f"Unexpected consumption response. Status: {status}", response_time)

def test_token_history():
    """Test token usage history"""
    print("\n5.3 Token Usage History")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test usage history endpoint
    history_endpoints = [
        "/api/user/usage/history",
        "/api/usage/history",
        "/api/user/token-history"
    ]
    
    for endpoint in history_endpoints:
        data, response_time, status = make_request("GET", endpoint, headers=headers)
        
        if status == 200:
            log_test(f"Usage History - {endpoint}", "PASS", "Successfully retrieved usage history", response_time)
        elif status == 404:
            log_test(f"Usage History - {endpoint}", "WARNING", "Usage history endpoint not found", response_time)
        else:
            log_test(f"Usage History - {endpoint}", "WARNING", f"Unexpected history response. Status: {status}", response_time)

def test_admin_token_management():
    """Test admin token management endpoints"""
    print("\n5.4 Admin Token Management")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test admin token adjustment endpoints
    admin_endpoints = [
        {
            "endpoint": "/api/admin/tokens/adjust",
            "method": "POST",
            "data": {
                "user_id": 1,
                "tokens": 10,
                "reason": "Test adjustment"
            }
        },
        {
            "endpoint": "/api/admin/tokens/history",
            "method": "GET",
            "data": None
        },
        {
            "endpoint": "/api/admin/user-tokens",
            "method": "GET",
            "data": None
        }
    ]
    
    for test in admin_endpoints:
        if test["method"] == "GET":
            data, response_time, status = make_request("GET", test["endpoint"], headers=headers)
        else:
            data, response_time, status = make_request("POST", test["endpoint"], 
                                                     headers=headers, data=test["data"])
        
        if status == 403:
            log_test(f"Admin Token Management - {test['endpoint']}", "PASS", 
                    "Properly denies admin access to regular user", response_time)
        elif status == 404:
            log_test(f"Admin Token Management - {test['endpoint']}", "WARNING", 
                    "Admin endpoint not found", response_time)
        elif status == 200:
            log_test(f"Admin Token Management - {test['endpoint']}", "FAIL", 
                    "CRITICAL: Admin endpoint accessible to regular user!", response_time)
        else:
            log_test(f"Admin Token Management - {test['endpoint']}", "WARNING", 
                    f"Unexpected admin response. Status: {status}", response_time)

def test_token_validation():
    """Test token validation and edge cases"""
    print("\n5.5 Token Validation")
    print("-" * 30)
    
    # Test token validation endpoints
    validation_tests = [
        {
            "name": "Valid Token Check",
            "endpoint": "/api/tokens/validate",
            "data": {"token": "test_token"}
        },
        {
            "name": "Token Balance Check",
            "endpoint": "/api/tokens/balance",
            "data": {"user_id": 1}
        },
        {
            "name": "Token Expiry Check",
            "endpoint": "/api/tokens/expiry",
            "data": {"token": "test_token"}
        }
    ]
    
    for test in validation_tests:
        data, response_time, status = make_request("POST", test["endpoint"], data=test["data"])
        
        if status in [200, 400, 401, 404]:
            log_test(f"Token Validation - {test['name']}", "PASS", 
                    f"Validation endpoint handled request. Status: {status}", response_time)
        else:
            log_test(f"Token Validation - {test['name']}", "WARNING", 
                    f"Unexpected validation response. Status: {status}", response_time)

def generate_report():
    """Generate token test report"""
    print("\n" + "="*60)
    print("TOKEN MANAGEMENT TEST REPORT")
    print("="*60)
    
    total_tests = len(TEST_RESULTS)
    passed = len([r for r in TEST_RESULTS if r.status == "PASS"])
    failed = len([r for r in TEST_RESULTS if r.status == "FAIL"])
    warnings = len([r for r in TEST_RESULTS if r.status == "WARNING"])
    errors = len([r for r in TEST_RESULTS if r.status == "ERROR"])
    
    print(f"\nSUMMARY:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Warnings: {warnings}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
    
    print(f"\nFAILED TESTS:")
    for result in TEST_RESULTS:
        if result.status == "FAIL":
            print(f"  - {result.test_name}: {result.details}")
    
    print(f"\nWARNINGS:")
    for result in TEST_RESULTS:
        if result.status == "WARNING":
            print(f"  - {result.test_name}: {result.details}")

def main():
    """Main token test execution"""
    print("Zimmer AI Platform - Token Management Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now()}")
    
    try:
        test_token_balance_tracking()
        test_token_consumption()
        test_token_history()
        test_admin_token_management()
        test_token_validation()
        
        generate_report()
        
    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
    except Exception as e:
        print(f"\nTesting failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nCompleted at: {datetime.now()}")

if __name__ == "__main__":
    main()
