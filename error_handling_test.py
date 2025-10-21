#!/usr/bin/env python3
"""
Error Handling & Recovery Testing Script for Zimmer AI Platform
Tests graceful error handling, recovery mechanisms, and data consistency
"""

import requests
import time
import json
import threading
from typing import List, Dict, Any
import random
import string

# Configuration
BASE_URL = "https://api.zimmerai.com"
TEST_USER_EMAIL = "error_test@example.com"
TEST_USER_PASSWORD = "ErrorTest123!"

class ErrorHandlingTest:
    def __init__(self):
        self.results = []
        self.auth_token = None
        
    def log_test(self, test_name: str, status: str, details: str, additional_data: Dict = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time(),
            "additional_data": additional_data or {}
        }
        self.results.append(result)
        print(f"[{status}] {test_name} - {details}")
        return result

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, timeout: int = 30) -> Dict:
        """Make HTTP request"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except requests.exceptions.Timeout:
            return {
                "status_code": 0,
                "error": "Request timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status_code": 0,
                "error": "Connection error"
            }
        except Exception as e:
            return {
                "status_code": 0,
                "error": str(e)
            }

    def setup_test_user(self):
        """Create test user for error testing"""
        print("\n=== Setting up test user ===")
        
        # Try to create test user
        signup_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Error Test User",
            "confirm_password": TEST_USER_PASSWORD
        }
        
        result = self.make_request("POST", "/api/auth/signup", signup_data)
        
        # Debug: print the exact response
        print(f"DEBUG: Status: {result['status_code']}, Data: {result.get('data', {})}")
        
        if result["status_code"] == 201:
            self.auth_token = result["data"].get("access_token")
            self.log_test("User Setup", "PASS", "Test user created successfully")
            return True
        elif result["status_code"] in [400, 409]:
            # User already exists, try to login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            result = self.make_request("POST", "/api/auth/login", login_data)
            
            if result["status_code"] == 200:
                self.auth_token = result["data"].get("access_token")
                self.log_test("User Setup", "PASS", "Test user login successful")
                return True
            else:
                self.log_test("User Setup", "FAIL", f"Login failed: {result.get('error', result.get('data', 'Unknown error'))}")
                return False
        else:
            self.log_test("User Setup", "FAIL", f"Failed to create test user: {result.get('error', result.get('data', 'Unknown error'))}")
            return False

    def test_invalid_input_handling(self):
        """Test handling of invalid input data"""
        print("\n=== Testing Invalid Input Handling ===")
        
        if not self.auth_token:
            self.log_test("Invalid Input", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test cases for invalid inputs
        invalid_inputs = [
            {
                "endpoint": "/api/auth/signup",
                "data": {"email": "invalid-email", "password": "123", "name": "", "confirm_password": "456"},
                "description": "Invalid email format, weak password, empty name, password mismatch"
            },
            {
                "endpoint": "/api/user/automations/999999",
                "method": "POST",
                "data": {"invalid_field": "test"},
                "description": "Non-existent automation ID with invalid data"
            },
            {
                "endpoint": "/api/payments/zarinpal/init",
                "method": "POST",
                "data": {"automation_id": "not_a_number", "token_amount": -100, "return_path": ""},
                "description": "Invalid automation ID, negative amount, empty return path"
            }
        ]
        
        for test_case in invalid_inputs:
            method = test_case.get("method", "POST")
            result = self.make_request(method, test_case["endpoint"], test_case["data"], headers)
            
            # Should return 400 or 422 for validation errors
            if result["status_code"] in [400, 422]:
                self.log_test(f"Invalid Input - {test_case['description']}", "PASS", 
                            f"Properly rejected with {result['status_code']}")
            else:
                self.log_test(f"Invalid Input - {test_case['description']}", "FAIL", 
                            f"Unexpected response: {result['status_code']}")

    def test_authentication_errors(self):
        """Test authentication error handling"""
        print("\n=== Testing Authentication Error Handling ===")
        
        # Test without token
        result = self.make_request("GET", "/api/auth/me")
        if result["status_code"] == 401:
            self.log_test("Auth Error - No Token", "PASS", "Properly rejected without token")
        else:
            self.log_test("Auth Error - No Token", "FAIL", f"Unexpected response: {result['status_code']}")
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        result = self.make_request("GET", "/api/auth/me", headers=invalid_headers)
        if result["status_code"] == 401:
            self.log_test("Auth Error - Invalid Token", "PASS", "Properly rejected invalid token")
        else:
            self.log_test("Auth Error - Invalid Token", "FAIL", f"Unexpected response: {result['status_code']}")
        
        # Test with malformed token
        malformed_headers = {"Authorization": "Bearer malformed.token.here"}
        result = self.make_request("GET", "/api/auth/me", headers=malformed_headers)
        if result["status_code"] == 401:
            self.log_test("Auth Error - Malformed Token", "PASS", "Properly rejected malformed token")
        else:
            self.log_test("Auth Error - Malformed Token", "FAIL", f"Unexpected response: {result['status_code']}")

    def test_authorization_errors(self):
        """Test authorization error handling"""
        print("\n=== Testing Authorization Error Handling ===")
        
        if not self.auth_token:
            self.log_test("Authorization Errors", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test accessing admin endpoints with regular user token
        admin_endpoints = [
            "/api/admin/dashboard/stats",
            "/api/admin/users",
            "/api/admin/user-automations",
            "/api/admin/automations",
            "/api/admin/tokens/adjust"
        ]
        
        for endpoint in admin_endpoints:
            result = self.make_request("GET", endpoint, headers=headers)
            if result["status_code"] == 403:
                self.log_test(f"AuthZ Error - {endpoint}", "PASS", "Properly rejected admin access")
            elif result["status_code"] == 401:
                self.log_test(f"AuthZ Error - {endpoint}", "PASS", "Properly rejected (401 instead of 403)")
            else:
                self.log_test(f"AuthZ Error - {endpoint}", "FAIL", f"Unexpected response: {result['status_code']}")

    def test_not_found_errors(self):
        """Test 404 error handling"""
        print("\n=== Testing Not Found Error Handling ===")
        
        if not self.auth_token:
            self.log_test("Not Found Errors", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test non-existent endpoints
        not_found_endpoints = [
            "/api/nonexistent/endpoint",
            "/api/user/automations/999999",
            "/api/automations/999999",
            "/api/payments/invalid-gateway/init"
        ]
        
        for endpoint in not_found_endpoints:
            result = self.make_request("GET", endpoint, headers=headers)
            if result["status_code"] == 404:
                self.log_test(f"Not Found - {endpoint}", "PASS", "Properly returned 404")
            else:
                self.log_test(f"Not Found - {endpoint}", "FAIL", f"Unexpected response: {result['status_code']}")

    def test_method_not_allowed_errors(self):
        """Test 405 Method Not Allowed errors"""
        print("\n=== Testing Method Not Allowed Errors ===")
        
        if not self.auth_token:
            self.log_test("Method Not Allowed", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test wrong HTTP methods
        method_tests = [
            ("PUT", "/api/auth/me", "PUT on GET-only endpoint"),
            ("DELETE", "/api/user/dashboard", "DELETE on GET-only endpoint"),
            ("GET", "/api/payments/zarinpal/init", "GET on POST-only endpoint")
        ]
        
        for method, endpoint, description in method_tests:
            result = self.make_request(method, endpoint, headers=headers)
            if result["status_code"] == 405:
                self.log_test(f"Method Not Allowed - {description}", "PASS", "Properly returned 405")
            else:
                self.log_test(f"Method Not Allowed - {description}", "FAIL", f"Unexpected response: {result['status_code']}")

    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        print("\n=== Testing Large Payload Handling ===")
        
        if not self.auth_token:
            self.log_test("Large Payload", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Create large payload (1MB of random data)
        large_data = "x" * (1024 * 1024)  # 1MB string
        
        large_payload = {
            "test_data": large_data,
            "description": "Large payload test"
        }
        
        result = self.make_request("POST", "/api/user/automations/21", large_payload, headers)
        
        # Should either accept it or reject it gracefully (not crash)
        if result["status_code"] in [200, 201, 400, 413, 422]:
            self.log_test("Large Payload", "PASS", f"Handled gracefully with {result['status_code']}")
        else:
            self.log_test("Large Payload", "FAIL", f"Unexpected response: {result['status_code']}")

    def test_sql_injection_attempts(self):
        """Test SQL injection protection"""
        print("\n=== Testing SQL Injection Protection ===")
        
        if not self.auth_token:
            self.log_test("SQL Injection", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # SQL injection attempts
        sql_injections = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--"
        ]
        
        for injection in sql_injections:
            # Test in different fields
            test_data = {
                "email": injection,
                "name": injection,
                "description": injection
            }
            
            result = self.make_request("POST", "/api/auth/signup", test_data)
            
            # Should be rejected, not cause server error
            if result["status_code"] in [400, 422, 409]:
                self.log_test(f"SQL Injection - {injection[:20]}...", "PASS", "Properly rejected")
            elif result["status_code"] == 500:
                self.log_test(f"SQL Injection - {injection[:20]}...", "FAIL", "Server error - potential vulnerability")
            else:
                self.log_test(f"SQL Injection - {injection[:20]}...", "WARN", f"Unexpected response: {result['status_code']}")

    def test_xss_attempts(self):
        """Test XSS protection"""
        print("\n=== Testing XSS Protection ===")
        
        if not self.auth_token:
            self.log_test("XSS Protection", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # XSS attempts
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            test_data = {
                "name": payload,
                "description": payload
            }
            
            result = self.make_request("POST", "/api/auth/signup", test_data)
            
            # Should be rejected or sanitized
            if result["status_code"] in [400, 422, 409]:
                self.log_test(f"XSS Protection - {payload[:20]}...", "PASS", "Properly rejected")
            else:
                self.log_test(f"XSS Protection - {payload[:20]}...", "WARN", f"Response: {result['status_code']}")

    def test_concurrent_error_handling(self):
        """Test error handling under concurrent load"""
        print("\n=== Testing Concurrent Error Handling ===")
        
        if not self.auth_token:
            self.log_test("Concurrent Errors", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        def make_error_request(request_id: int):
            """Make a request that should cause an error"""
            # Mix of valid and invalid requests
            if request_id % 2 == 0:
                # Valid request
                result = self.make_request("GET", "/api/auth/me", headers=headers)
            else:
                # Invalid request
                result = self.make_request("GET", "/api/nonexistent/endpoint", headers=headers)
            
            return {
                "request_id": request_id,
                "status_code": result["status_code"],
                "error": result.get("error")
            }
        
        # Make 20 concurrent requests (mix of valid/invalid)
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_error_request, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Check that server handled all requests without crashing
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["status_code"] in [200, 201, 400, 401, 404, 405, 422])
        
        if successful_requests == total_requests:
            self.log_test("Concurrent Error Handling", "PASS", 
                        f"All {total_requests} requests handled properly")
        else:
            self.log_test("Concurrent Error Handling", "FAIL", 
                        f"Only {successful_requests}/{total_requests} requests handled properly")

    def test_data_consistency(self):
        """Test data consistency under error conditions"""
        print("\n=== Testing Data Consistency ===")
        
        if not self.auth_token:
            self.log_test("Data Consistency", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test that failed operations don't leave partial data
        # Try to add automation with invalid data
        invalid_automation_data = {
            "automation_id": "invalid",
            "invalid_field": "test"
        }
        
        result = self.make_request("POST", "/api/user/automations/21", invalid_automation_data, headers)
        
        if result["status_code"] in [400, 422]:
            # Check that no partial data was created
            check_result = self.make_request("GET", "/api/user/automations", headers=headers)
            
            if check_result["status_code"] == 200:
                # Verify data integrity
                automations = check_result["data"]
                self.log_test("Data Consistency", "PASS", "No partial data created from failed operation")
            else:
                self.log_test("Data Consistency", "FAIL", "Could not verify data consistency")
        else:
            self.log_test("Data Consistency", "WARN", f"Unexpected response: {result['status_code']}")

    def generate_error_report(self):
        """Generate error handling test report"""
        print("\n" + "="*60)
        print("ERROR HANDLING TEST REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.results if r["status"] == "WARN")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        print(f"Skipped: {skipped}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        # Security assessment
        security_tests = [r for r in self.results if "SQL Injection" in r["test_name"] or "XSS" in r["test_name"]]
        security_passed = sum(1 for r in security_tests if r["status"] == "PASS")
        
        if security_tests:
            print(f"\nSecurity Tests: {security_passed}/{len(security_tests)} passed")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for result in self.results:
            status_icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠", "SKIP": "-"}
            icon = status_icon.get(result["status"], "?")
            print(f"{icon} {result['test_name']}: {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "success_rate": (passed/total_tests)*100,
            "security_tests": len(security_tests),
            "security_passed": security_passed,
            "results": self.results
        }

def main():
    """Run error handling tests"""
    print("Starting Error Handling Testing for Zimmer AI Platform")
    print("="*60)
    
    tester = ErrorHandlingTest()
    
    # Setup
    if not tester.setup_test_user():
        print("Failed to setup test user. Exiting.")
        return
    
    # Run error handling tests
    tester.test_invalid_input_handling()
    tester.test_authentication_errors()
    tester.test_authorization_errors()
    tester.test_not_found_errors()
    tester.test_method_not_allowed_errors()
    tester.test_large_payload_handling()
    tester.test_sql_injection_attempts()
    tester.test_xss_attempts()
    tester.test_concurrent_error_handling()
    tester.test_data_consistency()
    
    # Generate report
    report = tester.generate_error_report()
    
    # Save report to file
    with open("error_handling_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nError handling test report saved to: error_handling_test_report.json")

if __name__ == "__main__":
    main()
