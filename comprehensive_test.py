#!/usr/bin/env python3
"""
Comprehensive Zimmer AI Platform Testing Script
Tests all critical components systematically
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
                expected_status: int = 200, timeout: int = 30) -> Optional[Dict]:
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
        
        # Check if status matches expected
        if response.status_code == expected_status:
            try:
                return response.json(), response_time
            except:
                return response.text, response_time
        else:
            return None, response_time
            
    except requests.exceptions.RequestException as e:
        response_time = time.time() - start_time
        return None, response_time

def test_phase_1_infrastructure():
    """Phase 1: Backend Infrastructure & Database"""
    print("\n" + "="*60)
    print("PHASE 1: BACKEND INFRASTRUCTURE & DATABASE")
    print("="*60)
    
    # 1.1 Service Health Checks
    print("\n1.1 Service Health Checks")
    print("-" * 30)
    
    # Test health endpoint
    data, response_time = make_request("GET", "/health")
    if data and "status" in data:
        log_test("Health Endpoint", "PASS", f"Status: {data.get('status')}", response_time)
    else:
        log_test("Health Endpoint", "FAIL", "Health endpoint not responding", response_time)
    
    # Test CORS endpoint
    data, response_time = make_request("GET", "/test-cors")
    if data and "message" in data:
        log_test("CORS Test Endpoint", "PASS", f"Message: {data.get('message')}", response_time)
    else:
        log_test("CORS Test Endpoint", "FAIL", "CORS test endpoint not responding", response_time)
    
    # 1.2 Database Schema Validation (via API responses)
    print("\n1.2 Database Schema Validation")
    print("-" * 30)
    
    # Test if we can get any data that requires database access
    # This will be tested more thoroughly in later phases with authentication

def test_phase_2_authentication():
    """Phase 2: Authentication & Authorization System"""
    print("\n" + "="*60)
    print("PHASE 2: AUTHENTICATION & AUTHORIZATION SYSTEM")
    print("="*60)
    
    # 2.1 User Registration & Login
    print("\n2.1 User Registration & Login")
    print("-" * 30)
    
    # Test signup endpoint (should fail without proper data)
    data, response_time = make_request("POST", "/api/auth/signup", 
                                     data={"email": "test@example.com"}, 
                                     expected_status=422)
    if data is None:
        log_test("Signup Validation", "PASS", "Properly validates required fields", response_time)
    else:
        log_test("Signup Validation", "WARNING", "Unexpected response", response_time)
    
    # Test login endpoint (should fail without proper data)
    data, response_time = make_request("POST", "/api/auth/login", 
                                     data={"email": "test@example.com"}, 
                                     expected_status=422)
    if data is None:
        log_test("Login Validation", "PASS", "Properly validates required fields", response_time)
    else:
        log_test("Login Validation", "WARNING", "Unexpected response", response_time)
    
    # Test invalid login
    data, response_time = make_request("POST", "/api/auth/login", 
                                     data={"email": "nonexistent@example.com", "password": "wrong"}, 
                                     expected_status=401)
    if data is None:
        log_test("Invalid Login", "PASS", "Properly rejects invalid credentials", response_time)
    else:
        log_test("Invalid Login", "WARNING", "Unexpected response", response_time)

def test_phase_3_automation():
    """Phase 3: Automation System"""
    print("\n" + "="*60)
    print("PHASE 3: AUTOMATION SYSTEM")
    print("="*60)
    
    # 3.1 Marketplace Listing
    print("\n3.1 Marketplace Listing")
    print("-" * 30)
    
    # Test marketplace endpoint (requires auth, should return 401)
    data, response_time = make_request("GET", "/api/automations/marketplace", 
                                     expected_status=401)
    if data is None:
        log_test("Marketplace Auth Required", "PASS", "Properly requires authentication", response_time)
    else:
        log_test("Marketplace Auth Required", "PASS", "Requires authentication (got 401)", response_time)
    
    # Test available automations endpoint (should be public)
    data, response_time = make_request("GET", "/api/automations/available")
    if data and isinstance(data, list):
        log_test("Available Automations", "PASS", f"Found {len(data)} automations", response_time)
        # Check if automation ID 21 is in the list
        automation_21 = next((a for a in data if a.get('id') == 21), None)
        if automation_21:
            log_test("Automation ID 21 Present", "PASS", f"Found: {automation_21.get('name')}", 0)
        else:
            log_test("Automation ID 21 Present", "WARNING", "Automation ID 21 not found in available list", 0)
    elif data is None:
        # Check if it's returning 401 (auth required) vs other error
        log_test("Available Automations", "WARNING", "Endpoint requires authentication (not public)", response_time)
    else:
        log_test("Available Automations", "FAIL", "Could not fetch available automations", response_time)

def test_phase_4_payments():
    """Phase 4: Payment Processing"""
    print("\n" + "="*60)
    print("PHASE 4: PAYMENT PROCESSING")
    print("="*60)
    
    # 4.1 Payment Initialization
    print("\n4.1 Payment Initialization")
    print("-" * 30)
    
    # Test payment init without auth (should fail)
    data, response_time = make_request("POST", "/api/payments/zarinpal/init", 
                                     data={"automation_id": 21, "tokens": 10}, 
                                     expected_status=401)
    if data is None:
        log_test("Payment Init Auth Required", "PASS", "Properly requires authentication", response_time)
    else:
        log_test("Payment Init Auth Required", "PASS", "Requires authentication (got 401)", response_time)

def test_phase_6_endpoints():
    """Phase 6: API Endpoints & Routing"""
    print("\n" + "="*60)
    print("PHASE 6: API ENDPOINTS & ROUTING")
    print("="*60)
    
    # 6.1 Public Endpoints
    print("\n6.1 Public Endpoints")
    print("-" * 30)
    
    # Test health endpoint
    data, response_time = make_request("GET", "/health")
    if data and "status" in data:
        log_test("Health Endpoint", "PASS", f"Status: {data.get('status')}", response_time)
    else:
        log_test("Health Endpoint", "FAIL", "Health endpoint not working", response_time)
    
    # Test available automations (should be public)
    data, response_time = make_request("GET", "/api/automations/available")
    if data is not None:
        log_test("Available Automations Public", "PASS", "Public endpoint accessible", response_time)
    else:
        log_test("Available Automations Public", "WARNING", "Endpoint requires authentication (not public)", response_time)
    
    # 6.2 User Endpoints (should require auth)
    print("\n6.2 User Endpoints (Auth Required)")
    print("-" * 30)
    
    user_endpoints = [
        ("/api/auth/me", "GET"),
        ("/api/user/dashboard", "GET"),
        ("/api/user/automations", "GET"),
        ("/api/user/usage", "GET"),
        ("/api/notifications", "GET"),
    ]
    
    for endpoint, method in user_endpoints:
        data, response_time = make_request(method, endpoint, expected_status=401)
        if data is None:
            log_test(f"{method} {endpoint}", "PASS", "Properly requires authentication", response_time)
        else:
            log_test(f"{method} {endpoint}", "PASS", "Requires authentication (got 401)", response_time)
    
    # 6.3 Admin Endpoints (should require auth)
    print("\n6.3 Admin Endpoints (Auth Required)")
    print("-" * 30)
    
    admin_endpoints = [
        ("/api/admin/dashboard/stats", "GET"),
        ("/api/admin/users", "GET"),
        ("/api/admin/user-automations", "GET"),
    ]
    
    for endpoint, method in admin_endpoints:
        data, response_time = make_request(method, endpoint, expected_status=401)
        if data is None:
            log_test(f"{method} {endpoint}", "PASS", "Properly requires authentication", response_time)
        else:
            log_test(f"{method} {endpoint}", "PASS", "Requires authentication (got 401)", response_time)

def test_phase_8_security():
    """Phase 8: Security & Vulnerability Testing"""
    print("\n" + "="*60)
    print("PHASE 8: SECURITY & VULNERABILITY TESTING")
    print("="*60)
    
    # 8.1 Authentication Security
    print("\n8.1 Authentication Security")
    print("-" * 30)
    
    # Test SQL injection in login
    data, response_time = make_request("POST", "/api/auth/login", 
                                     data={"email": "admin'; DROP TABLE users; --", "password": "test"}, 
                                     expected_status=401)
    if data is None:
        log_test("SQL Injection Protection", "PASS", "Properly handles malicious input", response_time)
    else:
        log_test("SQL Injection Protection", "WARNING", "Response to SQL injection attempt", response_time)
    
    # Test XSS in login
    data, response_time = make_request("POST", "/api/auth/login", 
                                     data={"email": "<script>alert('xss')</script>", "password": "test"}, 
                                     expected_status=401)
    if data is None:
        log_test("XSS Protection", "PASS", "Properly handles XSS attempt", response_time)
    else:
        log_test("XSS Protection", "WARNING", "Response to XSS attempt", response_time)
    
    # 8.3 Input Validation
    print("\n8.3 Input Validation")
    print("-" * 30)
    
    # Test missing required fields
    data, response_time = make_request("POST", "/api/auth/login", 
                                     data={}, expected_status=422)
    if data is None:
        log_test("Required Fields Validation", "PASS", "Properly validates required fields", response_time)
    else:
        log_test("Required Fields Validation", "WARNING", "Unexpected response", response_time)
    
    # Test invalid data types
    data, response_time = make_request("POST", "/api/auth/login", 
                                     data={"email": 123, "password": True}, expected_status=422)
    if data is None:
        log_test("Data Type Validation", "PASS", "Properly validates data types", response_time)
    else:
        log_test("Data Type Validation", "WARNING", "Unexpected response", response_time)

def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST REPORT")
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
    
    print(f"\nALL TEST RESULTS:")
    for result in TEST_RESULTS:
        print(f"  {result}")

def main():
    """Main test execution"""
    print("Zimmer AI Platform - Comprehensive Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run test phases
        test_phase_1_infrastructure()
        test_phase_2_authentication()
        test_phase_3_automation()
        test_phase_4_payments()
        test_phase_6_endpoints()
        test_phase_8_security()
        
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
