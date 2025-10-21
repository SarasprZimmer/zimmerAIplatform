#!/usr/bin/env python3
"""
Performance Testing Script for Zimmer AI Platform
Tests response times, database queries, and concurrent request handling
"""

import requests
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import statistics

# Configuration
BASE_URL = "https://api.zimmerai.com"
TEST_USER_EMAIL = "perf_test@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

class PerformanceTest:
    def __init__(self):
        self.results = []
        self.auth_token = None
        
    def log_test(self, test_name: str, status: str, details: str, response_time: float = 0.0, additional_data: Dict = None):
        """Log test result with performance metrics"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": time.time(),
            "additional_data": additional_data or {}
        }
        self.results.append(result)
        print(f"[{status}] {test_name} - {details} ({response_time:.3f}s)")
        return result

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
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

    def setup_test_user(self):
        """Create test user for performance testing"""
        print("\n=== Setting up test user ===")
        
        # Try to create test user
        signup_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Performance Test User",
            "confirm_password": TEST_USER_PASSWORD
        }
        
        result = self.make_request("POST", "/api/auth/signup", signup_data)
        
        # Debug: print the exact response
        print(f"DEBUG: Status: {result['status_code']}, Data: {result.get('data', {})}")
        
        if result["status_code"] == 201:
            self.log_test("User Signup", "PASS", "Test user created successfully", result["response_time"])
            # Use the token from signup for login
            self.auth_token = result["data"].get("access_token")
            return True
        elif result["status_code"] in [400, 409]:
            # Check if it's a "user already exists" error
            error_msg = str(result.get("data", ""))
            if "already exists" in error_msg or "وجود دارد" in error_msg:
                self.log_test("User Signup", "PASS", "Test user already exists", result["response_time"])
            else:
                self.log_test("User Signup", "FAIL", f"Failed to create test user: {error_msg}", result["response_time"])
                return False
        else:
            self.log_test("User Signup", "FAIL", f"Failed to create test user: {result.get('error', result.get('data', 'Unknown error'))}", result["response_time"])
            return False
        
        # Login to get auth token
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        result = self.make_request("POST", "/api/auth/login", login_data)
        
        if result["status_code"] == 200:
            self.auth_token = result["data"].get("access_token")
            self.log_test("User Login", "PASS", "Login successful", result["response_time"])
            return True
        else:
            self.log_test("User Login", "FAIL", f"Login failed: {result.get('error', result.get('data', 'Unknown error'))}", result["response_time"])
            return False

    def test_endpoint_performance(self):
        """Test response times for all major endpoints"""
        print("\n=== Testing Endpoint Performance ===")
        
        if not self.auth_token:
            self.log_test("Endpoint Performance", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test endpoints with expected response times
        endpoints = [
            ("GET", "/health", None, "Health check", 0.5),
            ("GET", "/api/auth/me", headers, "User info", 1.0),
            ("GET", "/api/user/dashboard", headers, "User dashboard", 2.0),
            ("GET", "/api/user/automations", headers, "User automations", 1.5),
            ("GET", "/api/user/usage", headers, "Token usage", 1.0),
            ("GET", "/api/automations/marketplace", None, "Marketplace", 2.0),
            ("GET", "/api/notifications", headers, "Notifications", 1.0),
        ]
        
        for method, endpoint, endpoint_headers, description, max_expected_time in endpoints:
            result = self.make_request(method, endpoint, headers=endpoint_headers)
            
            if result["status_code"] in [200, 201]:
                if result["response_time"] <= max_expected_time:
                    self.log_test(f"Performance - {description}", "PASS", 
                                f"Response time within limits", result["response_time"],
                                {"max_expected": max_expected_time})
                else:
                    self.log_test(f"Performance - {description}", "WARN", 
                                f"Response time exceeds limits", result["response_time"],
                                {"max_expected": max_expected_time})
            else:
                self.log_test(f"Performance - {description}", "FAIL", 
                            f"HTTP {result['status_code']}", result["response_time"])

    def test_concurrent_requests(self):
        """Test system under concurrent load"""
        print("\n=== Testing Concurrent Requests ===")
        
        if not self.auth_token:
            self.log_test("Concurrent Requests", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        def make_concurrent_request(request_id: int):
            """Make a single concurrent request"""
            start_time = time.time()
            result = self.make_request("GET", "/api/auth/me", headers=headers)
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "status_code": result["status_code"],
                "response_time": result["response_time"],
                "success": result["status_code"] == 200
            }
        
        # Test with 10 concurrent requests
        concurrent_requests = 10
        print(f"Making {concurrent_requests} concurrent requests...")
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(concurrent_requests)]
            results = [future.result() for future in as_completed(futures)]
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_requests = sum(1 for r in results if r["success"])
        response_times = [r["response_time"] for r in results]
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        if successful_requests == concurrent_requests:
            self.log_test("Concurrent Requests", "PASS", 
                        f"All {concurrent_requests} requests successful", total_time,
                        {
                            "successful": successful_requests,
                            "total": concurrent_requests,
                            "avg_response_time": avg_response_time,
                            "max_response_time": max_response_time,
                            "min_response_time": min_response_time
                        })
        else:
            self.log_test("Concurrent Requests", "FAIL", 
                        f"Only {successful_requests}/{concurrent_requests} requests successful", total_time,
                        {
                            "successful": successful_requests,
                            "total": concurrent_requests,
                            "avg_response_time": avg_response_time,
                            "max_response_time": max_response_time,
                            "min_response_time": min_response_time
                        })

    def test_database_query_performance(self):
        """Test database-heavy operations"""
        print("\n=== Testing Database Query Performance ===")
        
        if not self.auth_token:
            self.log_test("Database Performance", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test endpoints that likely involve complex database queries
        db_heavy_endpoints = [
            ("GET", "/api/user/usage", "Token usage history"),
            ("GET", "/api/user/automations", "User automations with joins"),
            ("GET", "/api/notifications", "User notifications"),
        ]
        
        for method, endpoint, description in db_heavy_endpoints:
            # Make multiple requests to test consistency
            response_times = []
            for i in range(3):
                result = self.make_request(method, endpoint, headers=headers)
                if result["status_code"] == 200:
                    response_times.append(result["response_time"])
                time.sleep(0.1)  # Small delay between requests
            
            if response_times:
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                if avg_time <= 2.0:  # 2 second threshold for DB queries
                    self.log_test(f"DB Performance - {description}", "PASS", 
                                f"Average response time acceptable", avg_time,
                                {"avg": avg_time, "max": max_time, "min": min_time})
                else:
                    self.log_test(f"DB Performance - {description}", "WARN", 
                                f"Average response time high", avg_time,
                                {"avg": avg_time, "max": max_time, "min": min_time})

    def test_memory_usage(self):
        """Test memory usage under load (simulated)"""
        print("\n=== Testing Memory Usage ===")
        
        if not self.auth_token:
            self.log_test("Memory Usage", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Make many requests to test memory handling
        request_count = 50
        response_times = []
        errors = 0
        
        print(f"Making {request_count} requests to test memory usage...")
        
        for i in range(request_count):
            result = self.make_request("GET", "/api/auth/me", headers=headers)
            response_times.append(result["response_time"])
            
            if result["status_code"] != 200:
                errors += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.05)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Check if response times degrade over time (memory leak indicator)
        first_half = response_times[:request_count//2]
        second_half = response_times[request_count//2:]
        
        first_half_avg = statistics.mean(first_half)
        second_half_avg = statistics.mean(second_half)
        
        degradation = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if errors == 0 and degradation < 50:  # Less than 50% degradation
            self.log_test("Memory Usage", "PASS", 
                        f"No significant performance degradation", avg_response_time,
                        {
                            "total_requests": request_count,
                            "errors": errors,
                            "avg_response_time": avg_response_time,
                            "max_response_time": max_response_time,
                            "performance_degradation": f"{degradation:.1f}%"
                        })
        else:
            self.log_test("Memory Usage", "WARN", 
                        f"Performance degradation or errors detected", avg_response_time,
                        {
                            "total_requests": request_count,
                            "errors": errors,
                            "avg_response_time": avg_response_time,
                            "max_response_time": max_response_time,
                            "performance_degradation": f"{degradation:.1f}%"
                        })

    def generate_performance_report(self):
        """Generate performance test report"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST REPORT")
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
        
        # Performance metrics summary
        response_times = [r["response_time"] for r in self.results if r["response_time"] > 0]
        if response_times:
            print(f"\nResponse Time Statistics:")
            print(f"Average: {statistics.mean(response_times):.3f}s")
            print(f"Median: {statistics.median(response_times):.3f}s")
            print(f"Min: {min(response_times):.3f}s")
            print(f"Max: {max(response_times):.3f}s")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for result in self.results:
            status_icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠", "SKIP": "-"}
            icon = status_icon.get(result["status"], "?")
            print(f"{icon} {result['test_name']}: {result['details']} ({result['response_time']:.3f}s)")
            
            if result["additional_data"]:
                for key, value in result["additional_data"].items():
                    print(f"    {key}: {value}")
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "success_rate": (passed/total_tests)*100,
            "response_times": response_times,
            "results": self.results
        }

def main():
    """Run performance tests"""
    print("Starting Performance Testing for Zimmer AI Platform")
    print("="*60)
    
    tester = PerformanceTest()
    
    # Setup
    if not tester.setup_test_user():
        print("Failed to setup test user. Exiting.")
        return
    
    # Run performance tests
    tester.test_endpoint_performance()
    tester.test_concurrent_requests()
    tester.test_database_query_performance()
    tester.test_memory_usage()
    
    # Generate report
    report = tester.generate_performance_report()
    
    # Save report to file
    with open("performance_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nPerformance test report saved to: performance_test_report.json")

if __name__ == "__main__":
    main()
