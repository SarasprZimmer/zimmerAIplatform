#!/usr/bin/env python3
"""
Security Testing Script
Tests authentication bypass, authorization, and input validation
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

def test_authentication_bypass():
    """Test authentication bypass vulnerabilities"""
    print("\n8.1 Authentication Security")
    print("-" * 30)
    
    # Test various invalid tokens
    invalid_tokens = [
        "invalid_token_12345",
        "Bearer invalid_token",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
        "",
        "null",
        "undefined",
        "Bearer ",
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid_signature"
    ]
    
    for token in invalid_tokens:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Test /api/auth/me endpoint
        data, response_time, status = make_request("GET", "/api/auth/me", headers=headers)
        
        if status == 200:
            log_test(f"Auth Bypass - {token[:20]}...", "FAIL", f"CRITICAL: Invalid token accepted! Status: {status}", response_time)
        elif status == 401:
            log_test(f"Auth Bypass - {token[:20]}...", "PASS", "Properly rejects invalid token", response_time)
        else:
            log_test(f"Auth Bypass - {token[:20]}...", "WARNING", f"Unexpected status: {status}", response_time)

def test_authorization_bypass():
    """Test authorization bypass attempts"""
    print("\n8.2 Authorization Security")
    print("-" * 30)
    
    # Test admin endpoints without admin token
    admin_endpoints = [
        "/api/admin/dashboard/stats",
        "/api/admin/users",
        "/api/admin/user-automations",
        "/api/admin/automations",
        "/api/admin/tokens/adjust"
    ]
    
    # Use a regular user token (not admin)
    login_data = {
        "email": "testuser1761038526@example.com",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        for endpoint in admin_endpoints:
            data, response_time, status = make_request("GET", endpoint, headers=headers)
            
            if status == 403:
                log_test(f"Admin Access - {endpoint}", "PASS", "Properly denies admin access to regular user", response_time)
            elif status == 401:
                log_test(f"Admin Access - {endpoint}", "PASS", "Requires authentication", response_time)
            else:
                log_test(f"Admin Access - {endpoint}", "FAIL", f"CRITICAL: Admin endpoint accessible! Status: {status}", response_time)

def test_input_validation():
    """Test input validation and injection attacks"""
    print("\n8.3 Input Validation")
    print("-" * 30)
    
    # Test SQL injection in login
    sql_injection_payloads = [
        "admin'; DROP TABLE users; --",
        "admin' OR '1'='1",
        "admin' UNION SELECT * FROM users --",
        "admin' OR 1=1 --",
        "'; DELETE FROM users; --"
    ]
    
    for payload in sql_injection_payloads:
        login_data = {
            "email": payload,
            "password": "test"
        }
        
        data, response_time, status = make_request("POST", "/api/auth/login", data=login_data)
        
        if status == 401 or status == 422:
            log_test(f"SQL Injection - {payload[:20]}...", "PASS", "Properly handles malicious input", response_time)
        else:
            log_test(f"SQL Injection - {payload[:20]}...", "WARNING", f"Unexpected response: {status}", response_time)
    
    # Test XSS in login
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "';alert('xss');//"
    ]
    
    for payload in xss_payloads:
        login_data = {
            "email": payload,
            "password": "test"
        }
        
        data, response_time, status = make_request("POST", "/api/auth/login", data=login_data)
        
        if status == 401 or status == 422:
            log_test(f"XSS Protection - {payload[:20]}...", "PASS", "Properly handles XSS attempt", response_time)
        else:
            log_test(f"XSS Protection - {payload[:20]}...", "WARNING", f"Unexpected response: {status}", response_time)

def test_data_validation():
    """Test data type and format validation"""
    print("\n8.4 Data Validation")
    print("-" * 30)
    
    # Test invalid data types
    invalid_data_tests = [
        {"email": 123, "password": "test"},
        {"email": "test@example.com", "password": True},
        {"email": None, "password": "test"},
        {"email": "test@example.com", "password": None},
        {"email": [], "password": "test"},
        {"email": "test@example.com", "password": []},
        {"email": {}, "password": "test"},
        {"email": "test@example.com", "password": {}},
    ]
    
    for i, test_data in enumerate(invalid_data_tests):
        data, response_time, status = make_request("POST", "/api/auth/login", data=test_data)
        
        if status == 422:
            log_test(f"Data Type Validation - Test {i+1}", "PASS", "Properly validates data types", response_time)
        else:
            log_test(f"Data Type Validation - Test {i+1}", "WARNING", f"Unexpected response: {status}", response_time)
    
    # Test missing required fields
    missing_field_tests = [
        {"email": "test@example.com"},  # missing password
        {"password": "test"},  # missing email
        {},  # missing both
    ]
    
    for i, test_data in enumerate(missing_field_tests):
        data, response_time, status = make_request("POST", "/api/auth/login", data=test_data)
        
        if status == 422:
            log_test(f"Required Fields - Test {i+1}", "PASS", "Properly validates required fields", response_time)
        else:
            log_test(f"Required Fields - Test {i+1}", "WARNING", f"Unexpected response: {status}", response_time)

def test_rate_limiting():
    """Test rate limiting and DoS protection"""
    print("\n8.5 Rate Limiting & DoS Protection")
    print("-" * 30)
    
    # Test rapid requests
    start_time = time.time()
    request_count = 0
    
    for i in range(20):  # Send 20 rapid requests
        data, response_time, status = make_request("GET", "/health")
        request_count += 1
        
        if status == 429:  # Rate limited
            log_test("Rate Limiting", "PASS", f"Rate limiting active after {request_count} requests", response_time)
            break
        elif status != 200:
            log_test("Rate Limiting", "WARNING", f"Unexpected status: {status} after {request_count} requests", response_time)
            break
    
    total_time = time.time() - start_time
    
    if request_count == 20 and total_time < 5:  # All requests went through quickly
        log_test("Rate Limiting", "WARNING", f"No rate limiting detected - {request_count} requests in {total_time:.2f}s", 0)
    elif request_count < 20:
        log_test("Rate Limiting", "PASS", f"Rate limiting triggered after {request_count} requests", 0)

def generate_report():
    """Generate security test report"""
    print("\n" + "="*60)
    print("SECURITY TEST REPORT")
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
    print(f"Security Score: {(passed/total_tests)*100:.1f}%")
    
    print(f"\nCRITICAL SECURITY ISSUES:")
    for result in TEST_RESULTS:
        if result.status == "FAIL":
            print(f"  🚨 {result.test_name}: {result.details}")
    
    print(f"\nSECURITY WARNINGS:")
    for result in TEST_RESULTS:
        if result.status == "WARNING":
            print(f"  ⚠️  {result.test_name}: {result.details}")

def main():
    """Main security test execution"""
    print("Zimmer AI Platform - Security Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now()}")
    
    try:
        test_authentication_bypass()
        test_authorization_bypass()
        test_input_validation()
        test_data_validation()
        test_rate_limiting()
        
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
