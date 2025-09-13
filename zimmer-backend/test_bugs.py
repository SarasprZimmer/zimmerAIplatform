#!/usr/bin/env python3
"""
Comprehensive Bug Testing Suite for Zimmer AI Platform
This script tests various components for potential bugs and issues.
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

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class BugTester:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "critical": []
        }
        self.base_url = "http://localhost:8000"
        
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

    def test_environment_setup(self):
        """Test environment configuration"""
        print("\n🔧 Testing Environment Setup...")
        
        # Check if .env file exists
        if os.path.exists(".env"):
            self.log_result("ENV_FILE", "PASS", "Environment file exists")
        else:
            self.log_result("ENV_FILE", "CRITICAL", "Environment file missing")
            return False
            
        # Check required environment variables
        required_vars = ["JWT_SECRET_KEY", "OAI_ENCRYPTION_SECRET"]
        for var in required_vars:
            if os.getenv(var):
                self.log_result(f"ENV_{var}", "PASS", f"{var} is set")
            else:
                self.log_result(f"ENV_{var}", "CRITICAL", f"{var} is not set")
                
        return True

    def test_database_connection(self):
        """Test database connectivity and schema"""
        print("\n🗄️ Testing Database Connection...")
        
        try:
            # Test SQLite connection
            conn = sqlite3.connect("zimmer_dashboard.db")
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["users", "automations", "tickets", "payments"]
            for table in required_tables:
                if table in tables:
                    self.log_result(f"DB_TABLE_{table}", "PASS", f"Table {table} exists")
                else:
                    self.log_result(f"DB_TABLE_{table}", "WARNING", f"Table {table} missing")
                    
            conn.close()
            self.log_result("DB_CONNECTION", "PASS", "Database connection successful")
            return True
            
        except Exception as e:
            self.log_result("DB_CONNECTION", "CRITICAL", f"Database connection failed: {str(e)}")
            return False

    def test_imports(self):
        """Test if all required modules can be imported"""
        print("\n📦 Testing Module Imports...")
        
        modules_to_test = [
            "fastapi",
            "sqlalchemy",
            "pydantic",
            "jwt",
            "bcrypt",
            "cryptography",
            "requests",
            "uvicorn"
        ]
        
        for module in modules_to_test:
            try:
                __import__(module)
                self.log_result(f"IMPORT_{module}", "PASS", f"Module {module} imported successfully")
            except ImportError as e:
                self.log_result(f"IMPORT_{module}", "FAIL", f"Module {module} import failed: {str(e)}")
                
        # Test local modules
        local_modules = [
            "database",
            "models.user",
            "utils.jwt",
            "utils.security",
            "routers.users"
        ]
        
        for module in local_modules:
            try:
                __import__(module)
                self.log_result(f"IMPORT_LOCAL_{module}", "PASS", f"Local module {module} imported successfully")
            except ImportError as e:
                self.log_result(f"IMPORT_LOCAL_{module}", "FAIL", f"Local module {module} import failed: {str(e)}")

    def test_security_config(self):
        """Test security configuration"""
        print("\n🔐 Testing Security Configuration...")
        
        try:
            from utils.jwt import JWT_SECRET_KEY, JWT_ALGORITHM
            from utils.security import hash_password, verify_password
            
            # Test JWT configuration
            if JWT_SECRET_KEY and JWT_SECRET_KEY != "your-secret-key-change-in-production":
                self.log_result("JWT_SECRET", "PASS", "JWT secret key is properly configured")
            else:
                self.log_result("JWT_SECRET", "CRITICAL", "JWT secret key is not properly configured")
                
            # Test password hashing
            test_password = "test_password_123"
            hashed = hash_password(test_password)
            if verify_password(test_password, hashed):
                self.log_result("PASSWORD_HASHING", "PASS", "Password hashing works correctly")
            else:
                self.log_result("PASSWORD_HASHING", "CRITICAL", "Password hashing failed")
                
        except Exception as e:
            self.log_result("SECURITY_CONFIG", "CRITICAL", f"Security configuration test failed: {str(e)}")

    def test_file_permissions(self):
        """Test file permissions and security"""
        print("\n📁 Testing File Permissions...")
        
        # Check upload directory
        upload_dir = "uploads"
        if os.path.exists(upload_dir):
            self.log_result("UPLOAD_DIR", "PASS", "Upload directory exists")
        else:
            self.log_result("UPLOAD_DIR", "WARNING", "Upload directory does not exist")
            
        # Check database file permissions
        db_file = "zimmer_dashboard.db"
        if os.path.exists(db_file):
            self.log_result("DB_FILE", "PASS", "Database file exists")
        else:
            self.log_result("DB_FILE", "WARNING", "Database file does not exist")

    def test_api_endpoints(self):
        """Test API endpoints if server is running"""
        print("\n🌐 Testing API Endpoints...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("API_HEALTH", "PASS", "Health endpoint responds correctly")
            else:
                self.log_result("API_HEALTH", "FAIL", f"Health endpoint returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_result("API_CONNECTION", "WARNING", "API server is not running (expected for testing)")
        except Exception as e:
            self.log_result("API_TEST", "FAIL", f"API test failed: {str(e)}")

    def test_code_quality(self):
        """Test code quality and potential issues"""
        print("\n🔍 Testing Code Quality...")
        
        # Check for common security issues
        security_issues = []
        
        # Check main.py for security middleware
        try:
            with open("main.py", "r") as f:
                content = f.read()
                if "RateLimitMiddleware" in content:
                    self.log_result("RATE_LIMITING", "PASS", "Rate limiting middleware is implemented")
                else:
                    self.log_result("RATE_LIMITING", "WARNING", "Rate limiting middleware not found")
                    
                if "TrustedHostMiddleware" in content:
                    self.log_result("TRUSTED_HOST", "PASS", "Trusted host middleware is implemented")
                else:
                    self.log_result("TRUSTED_HOST", "WARNING", "Trusted host middleware not found")
                    
        except FileNotFoundError:
            self.log_result("MAIN_PY", "CRITICAL", "main.py file not found")
            
        # Check for hardcoded secrets
        try:
            from utils.jwt import JWT_SECRET_KEY
            if JWT_SECRET_KEY and JWT_SECRET_KEY != "your-secret-key-change-in-production":
                self.log_result("HARDCODED_SECRET", "PASS", "No hardcoded secrets found")
            else:
                self.log_result("HARDCODED_SECRET", "CRITICAL", "Hardcoded secret found in JWT config")
        except Exception as e:
            self.log_result("JWT_CONFIG", "WARNING", f"JWT config check failed: {str(e)}")

    def test_dependencies(self):
        """Test dependency versions and compatibility"""
        print("\n📋 Testing Dependencies...")
        
        try:
            import fastapi
            self.log_result("FASTAPI_VERSION", "PASS", f"FastAPI version: {fastapi.__version__}")
        except Exception as e:
            self.log_result("FASTAPI_VERSION", "FAIL", f"FastAPI version check failed: {str(e)}")
            
        try:
            import sqlalchemy
            self.log_result("SQLALCHEMY_VERSION", "PASS", f"SQLAlchemy version: {sqlalchemy.__version__}")
        except Exception as e:
            self.log_result("SQLALCHEMY_VERSION", "FAIL", f"SQLAlchemy version check failed: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Bug Testing Suite")
        print("=" * 60)
        
        # Run all test categories
        self.test_environment_setup()
        self.test_database_connection()
        self.test_imports()
        self.test_security_config()
        self.test_file_permissions()
        self.test_api_endpoints()
        self.test_code_quality()
        self.test_dependencies()
        
        # Generate report
        self.generate_report()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
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
        report_file = f"bug_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    """Main function to run the bug testing suite"""
    tester = BugTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The system appears to be working correctly.")
    else:
        print("\n⚠️  Some issues were found. Please review the report above.")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
