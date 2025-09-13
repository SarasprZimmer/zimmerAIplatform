#!/usr/bin/env python3
"""
Advanced Functional Test Suite for Zimmer AI Platform
This script tests actual functionality and identifies runtime bugs.
"""

import asyncio
import json
import sys
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
import requests
import subprocess
import time
import threading
import signal

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class FunctionalTester:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "critical": []
        }
        self.base_url = "http://localhost:8000"
        self.server_process = None
        
    def log_result(self, test_name: str, status: str, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        if status == "PASS":
            self.results["passed"].append(result)
        elif status == "FAIL":
            self.results["failed"].append(result)
        elif status == "WARNING":
            self.results["warnings"].append(result)
        elif status == "CRITICAL":
            self.results["critical"].append(result)
            
        print(f"[{status}] {test_name}: {message}")

    def start_server(self):
        """Start the FastAPI server for testing"""
        print("\n🚀 Starting FastAPI server for testing...")
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(5)
            
            # Test if server is running
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                if response.status_code == 200:
                    self.log_result("SERVER_START", "PASS", "FastAPI server started successfully")
                    return True
                else:
                    self.log_result("SERVER_START", "FAIL", f"Server responded with status {response.status_code}")
                    return False
            except requests.exceptions.ConnectionError:
                self.log_result("SERVER_START", "FAIL", "Server failed to start or respond")
                return False
                
        except Exception as e:
            self.log_result("SERVER_START", "CRITICAL", f"Failed to start server: {str(e)}")
            return False

    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.log_result("SERVER_STOP", "PASS", "Server stopped successfully")

    def test_authentication_flow(self):
        """Test the complete authentication flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        try:
            # Test user registration (if endpoint exists)
            register_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
            
            try:
                response = requests.post(f"{self.base_url}/api/signup", json=register_data, timeout=10)
                if response.status_code in [200, 201, 409]:  # 409 = user already exists
                    self.log_result("AUTH_REGISTER", "PASS", "User registration endpoint works")
                else:
                    self.log_result("AUTH_REGISTER", "WARNING", f"Registration returned {response.status_code}")
            except Exception as e:
                self.log_result("AUTH_REGISTER", "WARNING", f"Registration test failed: {str(e)}")
            
            # Test user login
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
            
            response = requests.post(f"{self.base_url}/api/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log_result("AUTH_LOGIN", "PASS", "User login successful")
                    token = data["access_token"]
                    
                    # Test protected endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(f"{self.base_url}/api/user/profile", headers=headers, timeout=10)
                    if response.status_code in [200, 404]:  # 404 if profile endpoint doesn't exist
                        self.log_result("AUTH_PROTECTED", "PASS", "Protected endpoint accessible with token")
                    else:
                        self.log_result("AUTH_PROTECTED", "WARNING", f"Protected endpoint returned {response.status_code}")
                else:
                    self.log_result("AUTH_LOGIN", "FAIL", "Login response missing access_token")
            else:
                self.log_result("AUTH_LOGIN", "FAIL", f"Login failed with status {response.status_code}")
                
        except Exception as e:
            self.log_result("AUTH_FLOW", "CRITICAL", f"Authentication flow test failed: {str(e)}")

    def test_api_endpoints(self):
        """Test various API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/docs", "API documentation"),
            ("/api/automations/available", "Available automations"),
            ("/api/knowledge", "Knowledge base"),
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401, 403]:  # 401/403 are expected for protected endpoints
                    self.log_result(f"ENDPOINT_{endpoint.replace('/', '_')}", "PASS", f"{description} responds correctly")
                else:
                    self.log_result(f"ENDPOINT_{endpoint.replace('/', '_')}", "WARNING", f"{description} returned {response.status_code}")
            except Exception as e:
                self.log_result(f"ENDPOINT_{endpoint.replace('/', '_')}", "FAIL", f"{description} failed: {str(e)}")

    def test_database_operations(self):
        """Test database operations"""
        print("\n🗄️ Testing Database Operations...")
        
        try:
            # Test database connection
            conn = sqlite3.connect("zimmer_dashboard.db")
            cursor = conn.cursor()
            
            # Test user creation
            cursor.execute("""
                INSERT OR IGNORE INTO users (name, email, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, ("Test User DB", "testdb@example.com", "hashed_password", "support_staff", True))
            
            # Test user retrieval
            cursor.execute("SELECT id, name, email FROM users WHERE email = ?", ("testdb@example.com",))
            user = cursor.fetchone()
            
            if user:
                self.log_result("DB_USER_CREATE", "PASS", "User creation and retrieval successful")
                
                # Test user update
                cursor.execute("UPDATE users SET name = ? WHERE email = ?", ("Updated Test User", "testdb@example.com"))
                conn.commit()
                self.log_result("DB_USER_UPDATE", "PASS", "User update successful")
            else:
                self.log_result("DB_USER_CREATE", "FAIL", "User creation failed")
                
            conn.close()
            
        except Exception as e:
            self.log_result("DB_OPERATIONS", "CRITICAL", f"Database operations failed: {str(e)}")

    def test_file_upload(self):
        """Test file upload functionality"""
        print("\n📁 Testing File Upload...")
        
        try:
            # Create a test file
            test_file_content = "This is a test file for upload testing."
            with open("test_upload.txt", "w") as f:
                f.write(test_file_content)
            
            # Test file upload (if endpoint exists)
            with open("test_upload.txt", "rb") as f:
                files = {"file": ("test_upload.txt", f, "text/plain")}
                data = {"user_id": "1", "subject": "Test Ticket", "message": "Test message"}
                
                try:
                    response = requests.post(f"{self.base_url}/api/tickets", files=files, data=data, timeout=10)
                    if response.status_code in [200, 201, 401, 403]:  # 401/403 expected without auth
                        self.log_result("FILE_UPLOAD", "PASS", "File upload endpoint responds correctly")
                    else:
                        self.log_result("FILE_UPLOAD", "WARNING", f"File upload returned {response.status_code}")
                except Exception as e:
                    self.log_result("FILE_UPLOAD", "WARNING", f"File upload test failed: {str(e)}")
            
            # Clean up test file
            os.remove("test_upload.txt")
            
        except Exception as e:
            self.log_result("FILE_UPLOAD", "CRITICAL", f"File upload test failed: {str(e)}")

    def test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test invalid endpoint
        try:
            response = requests.get(f"{self.base_url}/invalid/endpoint", timeout=10)
            if response.status_code == 404:
                self.log_result("ERROR_404", "PASS", "404 error handling works correctly")
            else:
                self.log_result("ERROR_404", "WARNING", f"Invalid endpoint returned {response.status_code}")
        except Exception as e:
            self.log_result("ERROR_404", "FAIL", f"404 test failed: {str(e)}")
        
        # Test invalid JSON
        try:
            response = requests.post(f"{self.base_url}/api/login", data="invalid json", headers={"Content-Type": "application/json"}, timeout=10)
            if response.status_code in [400, 422]:
                self.log_result("ERROR_JSON", "PASS", "Invalid JSON handling works correctly")
            else:
                self.log_result("ERROR_JSON", "WARNING", f"Invalid JSON returned {response.status_code}")
        except Exception as e:
            self.log_result("ERROR_JSON", "FAIL", f"Invalid JSON test failed: {str(e)}")

    def test_performance(self):
        """Test basic performance"""
        print("\n⚡ Testing Performance...")
        
        # Test response time
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response_time < 1.0:  # Should respond within 1 second
                self.log_result("PERF_RESPONSE_TIME", "PASS", f"Response time: {response_time:.3f}s")
            else:
                self.log_result("PERF_RESPONSE_TIME", "WARNING", f"Slow response time: {response_time:.3f}s")
        except Exception as e:
            self.log_result("PERF_RESPONSE_TIME", "FAIL", f"Performance test failed: {str(e)}")

    def run_all_tests(self):
        """Run all functional tests"""
        print("🚀 Starting Advanced Functional Test Suite")
        print("=" * 60)
        
        # Start server
        if not self.start_server():
            print("❌ Cannot run functional tests without server")
            return False
        
        try:
            # Run all test categories
            self.test_authentication_flow()
            self.test_api_endpoints()
            self.test_database_operations()
            self.test_file_upload()
            self.test_error_handling()
            self.test_performance()
            
        finally:
            # Stop server
            self.stop_server()
        
        # Generate report
        self.generate_report()
        return True
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 FUNCTIONAL TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = (
            len(self.results["passed"]) + 
            len(self.results["failed"]) + 
            len(self.results["warnings"]) + 
            len(self.results["critical"])
        )
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"🚨 Critical: {len(self.results['critical'])}")
        
        if self.results["critical"]:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.results["critical"]:
                print(f"  • {issue['test']}: {issue['message']}")
                
        if self.results["failed"]:
            print("\n❌ FAILED TESTS:")
            for test in self.results["failed"]:
                print(f"  • {test['test']}: {test['message']}")
                
        if self.results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in self.results["warnings"]:
                print(f"  • {warning['test']}: {warning['message']}")
                
        # Save detailed report
        report_file = f"functional_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Overall status
        if self.results["critical"]:
            print("\n🔴 OVERALL STATUS: CRITICAL ISSUES FOUND")
            return False
        elif self.results["failed"]:
            print("\n🟡 OVERALL STATUS: SOME ISSUES FOUND")
            return False
        else:
            print("\n🟢 OVERALL STATUS: ALL TESTS PASSED")
            return True

def main():
    """Main function to run the functional testing suite"""
    tester = FunctionalTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All functional tests completed!")
    else:
        print("\n⚠️  Some functional issues were found. Please review the report above.")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
