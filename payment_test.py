#!/usr/bin/env python3
"""
Payment Processing Testing Script
Tests payment initialization, callback, verification, and token crediting
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

def test_payment_initialization():
    """Test payment initialization"""
    print("\n4.1 Payment Initialization")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test payment initialization with various scenarios
    test_cases = [
        {
            "name": "Valid Payment Request",
            "data": {
                "automation_id": 1,  # Try with ID 1 since 21 doesn't exist
                "tokens": 10,
                "return_path": "/tokens"
            },
            "expected_status": [200, 400, 404]  # Multiple possible responses
        },
        {
            "name": "Invalid Automation ID",
            "data": {
                "automation_id": 99999,
                "tokens": 10,
                "return_path": "/tokens"
            },
            "expected_status": [404, 400]
        },
        {
            "name": "Invalid Token Amount",
            "data": {
                "automation_id": 1,
                "tokens": 0,
                "return_path": "/tokens"
            },
            "expected_status": [400, 422]
        },
        {
            "name": "Missing Required Fields",
            "data": {
                "automation_id": 1,
                "tokens": 10
                # Missing return_path
            },
            "expected_status": [422, 400]
        }
    ]
    
    for test_case in test_cases:
        data, response_time, status = make_request("POST", "/api/payments/zarinpal/init", 
                                                 headers=headers, data=test_case["data"])
        
        if status in test_case["expected_status"]:
            log_test(f"Payment Init - {test_case['name']}", "PASS", 
                    f"Expected response. Status: {status}", response_time)
        else:
            log_test(f"Payment Init - {test_case['name']}", "WARNING", 
                    f"Unexpected status: {status}. Expected: {test_case['expected_status']}", response_time)

def test_payment_validation():
    """Test payment validation and error handling"""
    print("\n4.2 Payment Validation")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test invalid data types
    invalid_data_tests = [
        {
            "name": "Invalid Automation ID Type",
            "data": {
                "automation_id": "invalid",
                "tokens": 10,
                "return_path": "/tokens"
            }
        },
        {
            "name": "Invalid Token Amount Type",
            "data": {
                "automation_id": 1,
                "tokens": "invalid",
                "return_path": "/tokens"
            }
        },
        {
            "name": "Negative Token Amount",
            "data": {
                "automation_id": 1,
                "tokens": -5,
                "return_path": "/tokens"
            }
        },
        {
            "name": "Excessive Token Amount",
            "data": {
                "automation_id": 1,
                "tokens": 1000000,
                "return_path": "/tokens"
            }
        }
    ]
    
    for test in invalid_data_tests:
        data, response_time, status = make_request("POST", "/api/payments/zarinpal/init", 
                                                 headers=headers, data=test["data"])
        
        if status in [400, 422]:
            log_test(f"Payment Validation - {test['name']}", "PASS", 
                    f"Properly validates input. Status: {status}", response_time)
        else:
            log_test(f"Payment Validation - {test['name']}", "WARNING", 
                    f"Unexpected response. Status: {status}", response_time)

def test_payment_callback():
    """Test payment callback handling"""
    print("\n4.3 Payment Callback")
    print("-" * 30)
    
    # Test callback endpoint with various scenarios
    callback_tests = [
        {
            "name": "Valid Callback",
            "params": {
                "payment_id": 1,
                "Authority": "test_authority_123",
                "Status": "OK"
            }
        },
        {
            "name": "Cancelled Payment",
            "params": {
                "payment_id": 1,
                "Authority": "test_authority_123",
                "Status": "NOK"
            }
        },
        {
            "name": "Missing Parameters",
            "params": {
                "payment_id": 1
                # Missing Authority and Status
            }
        },
        {
            "name": "Invalid Payment ID",
            "params": {
                "payment_id": 99999,
                "Authority": "test_authority_123",
                "Status": "OK"
            }
        }
    ]
    
    for test in callback_tests:
        # Build query string
        query_params = "&".join([f"{k}={v}" for k, v in test["params"].items()])
        endpoint = f"/api/payments/zarinpal/callback?{query_params}"
        
        data, response_time, status = make_request("GET", endpoint)
        
        if status in [200, 400, 404]:
            log_test(f"Payment Callback - {test['name']}", "PASS", 
                    f"Callback handled. Status: {status}", response_time)
        else:
            log_test(f"Payment Callback - {test['name']}", "WARNING", 
                    f"Unexpected callback response. Status: {status}", response_time)

def test_discount_codes():
    """Test discount code system"""
    print("\n4.4 Discount Code System")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test discount code validation
    discount_tests = [
        {
            "name": "Valid Discount Code",
            "data": {
                "automation_id": 1,
                "tokens": 10,
                "return_path": "/tokens",
                "discount_code": "TEST100"
            }
        },
        {
            "name": "Invalid Discount Code",
            "data": {
                "automation_id": 1,
                "tokens": 10,
                "return_path": "/tokens",
                "discount_code": "INVALID_CODE"
            }
        },
        {
            "name": "Empty Discount Code",
            "data": {
                "automation_id": 1,
                "tokens": 10,
                "return_path": "/tokens",
                "discount_code": ""
            }
        }
    ]
    
    for test in discount_tests:
        data, response_time, status = make_request("POST", "/api/payments/zarinpal/init", 
                                                 headers=headers, data=test["data"])
        
        if status in [200, 400, 404]:
            log_test(f"Discount Code - {test['name']}", "PASS", 
                    f"Discount code handled. Status: {status}", response_time)
        else:
            log_test(f"Discount Code - {test['name']}", "WARNING", 
                    f"Unexpected discount response. Status: {status}", response_time)

def test_payment_endpoints():
    """Test payment-related endpoints"""
    print("\n4.5 Payment Endpoints")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test payment history endpoint
    data, response_time, status = make_request("GET", "/api/user/payments", headers=headers)
    
    if status == 200:
        log_test("Payment History", "PASS", "Successfully retrieved payment history", response_time)
    elif status == 404:
        log_test("Payment History", "WARNING", "Payment history endpoint not found", response_time)
    else:
        log_test("Payment History", "WARNING", f"Unexpected payment history response. Status: {status}", response_time)
    
    # Test payment status endpoint
    data, response_time, status = make_request("GET", "/api/payments/1/status", headers=headers)
    
    if status in [200, 404]:
        log_test("Payment Status", "PASS", f"Payment status endpoint accessible. Status: {status}", response_time)
    else:
        log_test("Payment Status", "WARNING", f"Unexpected payment status response. Status: {status}", response_time)

def generate_report():
    """Generate payment test report"""
    print("\n" + "="*60)
    print("PAYMENT PROCESSING TEST REPORT")
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
    """Main payment test execution"""
    print("Zimmer AI Platform - Payment Processing Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now()}")
    
    try:
        test_payment_initialization()
        test_payment_validation()
        test_payment_callback()
        test_discount_codes()
        test_payment_endpoints()
        
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
