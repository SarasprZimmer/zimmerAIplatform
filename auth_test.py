#!/usr/bin/env python3
"""
Authentication Testing Script
Tests user registration, login, token management, and role-based access
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BASE_URL = "https://api.zimmerai.com"
TEST_RESULTS = []
TEST_USERS = []

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

def make_request(method: str, endpoint: str, headers: Dict = None, data: Dict = None, 
                expected_status: int = 200, timeout: int = 30) -> tuple:
    """Make HTTP request and return (response_data, response_time, actual_status)"""
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

def test_user_registration():
    """Test user registration flow"""
    print("\n2.1 User Registration & Login")
    print("-" * 30)
    
    # Generate unique test user
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    test_password = "TestPassword123!"
    test_name = f"Test User {timestamp}"
    
    # Test signup with valid data
    signup_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name,
        "confirm_password": test_password
    }
    
    data, response_time, status = make_request("POST", "/api/auth/signup", data=signup_data)
    
    if status == 201 or status == 200:
        log_test("User Registration", "PASS", f"Successfully created user {test_email}", response_time)
        TEST_USERS.append({
            "email": test_email,
            "password": test_password,
            "name": test_name,
            "created": True
        })
        return test_email, test_password
    elif status == 409:
        log_test("User Registration", "WARNING", f"User {test_email} already exists", response_time)
        return test_email, test_password
    else:
        log_test("User Registration", "FAIL", f"Failed to create user. Status: {status}, Response: {data}", response_time)
        return None, None

def test_user_login(email: str, password: str):
    """Test user login flow"""
    login_data = {
        "email": email,
        "password": password
    }
    
    data, response_time, status = make_request("POST", "/api/auth/login", data=login_data)
    
    if status == 200 and data and "access_token" in data:
        log_test("User Login", "PASS", f"Successfully logged in user {email}", response_time)
        return data["access_token"]
    else:
        log_test("User Login", "FAIL", f"Failed to login user. Status: {status}, Response: {data}", response_time)
        return None

def test_authenticated_endpoints(token: str):
    """Test endpoints that require authentication"""
    print("\n2.2 Authenticated Endpoints")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /api/auth/me
    data, response_time, status = make_request("GET", "/api/auth/me", headers=headers)
    if status == 200 and data:
        log_test("Get User Info", "PASS", f"Retrieved user info: {data.get('email', 'unknown')}", response_time)
    else:
        log_test("Get User Info", "FAIL", f"Failed to get user info. Status: {status}", response_time)
    
    # Test /api/user/dashboard
    data, response_time, status = make_request("GET", "/api/user/dashboard", headers=headers)
    if status == 200 and data:
        log_test("User Dashboard", "PASS", "Successfully retrieved dashboard data", response_time)
    else:
        log_test("User Dashboard", "FAIL", f"Failed to get dashboard. Status: {status}", response_time)
    
    # Test /api/user/automations
    data, response_time, status = make_request("GET", "/api/user/automations", headers=headers)
    if status == 200 and data is not None:
        log_test("User Automations", "PASS", f"Retrieved user automations", response_time)
    else:
        log_test("User Automations", "FAIL", f"Failed to get user automations. Status: {status}", response_time)
    
    # Test /api/user/usage
    data, response_time, status = make_request("GET", "/api/user/usage", headers=headers)
    if status == 200 and data is not None:
        log_test("User Usage", "PASS", "Successfully retrieved usage data", response_time)
    else:
        log_test("User Usage", "FAIL", f"Failed to get usage data. Status: {status}", response_time)
    
    # Test /api/notifications
    data, response_time, status = make_request("GET", "/api/notifications", headers=headers)
    if status == 200 and data is not None:
        log_test("User Notifications", "PASS", "Successfully retrieved notifications", response_time)
    else:
        log_test("User Notifications", "FAIL", f"Failed to get notifications. Status: {status}", response_time)

def test_automation_marketplace(token: str):
    """Test automation marketplace with authentication"""
    print("\n3.1 Automation Marketplace (Authenticated)")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test marketplace endpoint with auth
    data, response_time, status = make_request("GET", "/api/automations/marketplace", headers=headers)
    if status == 200 and data and "automations" in data:
        automations = data["automations"]
        log_test("Marketplace with Auth", "PASS", f"Found {len(automations)} automations", response_time)
        
        # Check if automation ID 21 is present
        automation_21 = next((a for a in automations if a.get('id') == 21), None)
        if automation_21:
            log_test("Automation ID 21 in Marketplace", "PASS", f"Found: {automation_21.get('name')}", 0)
        else:
            log_test("Automation ID 21 in Marketplace", "WARNING", "Automation ID 21 not found in marketplace", 0)
    else:
        log_test("Marketplace with Auth", "FAIL", f"Failed to get marketplace. Status: {status}", response_time)
    
    # Test available automations endpoint
    data, response_time, status = make_request("GET", "/api/automations/available", headers=headers)
    if status == 200 and data and isinstance(data, list):
        log_test("Available Automations with Auth", "PASS", f"Found {len(data)} available automations", response_time)
    else:
        log_test("Available Automations with Auth", "FAIL", f"Failed to get available automations. Status: {status}", response_time)

def test_automation_addition(token: str):
    """Test adding automation to user account"""
    print("\n3.4 User Automation Creation")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to add automation ID 21 to user account
    data, response_time, status = make_request("POST", "/api/user/automations/21", headers=headers)
    
    if status == 200 or status == 201:
        log_test("Add Automation to User", "PASS", "Successfully added automation to user account", response_time)
    elif status == 400 and data and "already has this automation" in str(data):
        log_test("Add Automation to User", "PASS", "User already has this automation (expected)", response_time)
    else:
        log_test("Add Automation to User", "FAIL", f"Failed to add automation. Status: {status}, Response: {data}", response_time)

def test_payment_initialization(token: str):
    """Test payment initialization with authentication"""
    print("\n4.1 Payment Initialization (Authenticated)")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    payment_data = {
        "automation_id": 21,
        "tokens": 10,
        "return_path": "/tokens"
    }
    
    data, response_time, status = make_request("POST", "/api/payments/zarinpal/init", 
                                             headers=headers, data=payment_data)
    
    if status == 200 and data and "authority" in data:
        log_test("Payment Initialization", "PASS", f"Successfully initialized payment. Authority: {data.get('authority', 'unknown')}", response_time)
    elif status == 400 and data and "unavailable for purchase" in str(data):
        log_test("Payment Initialization", "WARNING", "Automation unavailable for purchase (may be expected)", response_time)
    else:
        log_test("Payment Initialization", "FAIL", f"Failed to initialize payment. Status: {status}, Response: {data}", response_time)

def test_invalid_token():
    """Test endpoints with invalid token"""
    print("\n2.3 Invalid Token Testing")
    print("-" * 30)
    
    headers = {"Authorization": "Bearer invalid_token_12345"}
    
    data, response_time, status = make_request("GET", "/api/auth/me", headers=headers)
    if status == 401:
        log_test("Invalid Token Rejection", "PASS", "Properly rejects invalid token", response_time)
    else:
        log_test("Invalid Token Rejection", "FAIL", f"Should reject invalid token. Status: {status}", response_time)

def generate_report():
    """Generate authentication test report"""
    print("\n" + "="*60)
    print("AUTHENTICATION TEST REPORT")
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
    
    print(f"\nTEST USERS CREATED:")
    for user in TEST_USERS:
        if user.get("created"):
            print(f"  - {user['email']}")
    
    print(f"\nFAILED TESTS:")
    for result in TEST_RESULTS:
        if result.status == "FAIL":
            print(f"  - {result.test_name}: {result.details}")
    
    print(f"\nWARNINGS:")
    for result in TEST_RESULTS:
        if result.status == "WARNING":
            print(f"  - {result.test_name}: {result.details}")

def main():
    """Main authentication test execution"""
    print("Zimmer AI Platform - Authentication Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now()}")
    
    try:
        # Test user registration
        email, password = test_user_registration()
        
        if email and password:
            # Test user login
            token = test_user_login(email, password)
            
            if token:
                # Test authenticated endpoints
                test_authenticated_endpoints(token)
                
                # Test automation marketplace
                test_automation_marketplace(token)
                
                # Test automation addition
                test_automation_addition(token)
                
                # Test payment initialization
                test_payment_initialization(token)
        
        # Test invalid token
        test_invalid_token()
        
        # Generate report
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
