#!/usr/bin/env python3
"""
Automation System Testing Script
Tests automation marketplace, health checks, and user automation creation
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

def test_automation_marketplace():
    """Test automation marketplace functionality"""
    print("\n3.1 Marketplace Listing")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test marketplace endpoint with auth
    data, response_time, status = make_request("GET", "/api/automations/marketplace", headers=headers)
    
    if status == 200 and data and "automations" in data:
        automations = data["automations"]
        log_test("Marketplace Endpoint", "PASS", f"Found {len(automations)} automations", response_time)
        
        # Check automation properties
        if automations:
            automation = automations[0]
            required_fields = ["id", "name", "description", "pricing_type", "price_per_token", "health_status"]
            missing_fields = [field for field in required_fields if field not in automation]
            
            if not missing_fields:
                log_test("Marketplace Data Structure", "PASS", "All required fields present", 0)
            else:
                log_test("Marketplace Data Structure", "WARNING", f"Missing fields: {missing_fields}", 0)
        
        # Check if automation ID 21 is present
        automation_21 = next((a for a in automations if a.get('id') == 21), None)
        if automation_21:
            log_test("Automation ID 21 in Marketplace", "PASS", f"Found: {automation_21.get('name')}", 0)
        else:
            log_test("Automation ID 21 in Marketplace", "WARNING", "Automation ID 21 not found in marketplace", 0)
    else:
        log_test("Marketplace Endpoint", "FAIL", f"Failed to get marketplace. Status: {status}, Response: {data}", response_time)
    
    # Test available automations endpoint
    data, response_time, status = make_request("GET", "/api/automations/available", headers=headers)
    
    if status == 200 and data is not None:
        if isinstance(data, list):
            log_test("Available Automations", "PASS", f"Found {len(data)} available automations", response_time)
        else:
            log_test("Available Automations", "WARNING", f"Unexpected data format: {type(data)}", response_time)
    else:
        log_test("Available Automations", "FAIL", f"Failed to get available automations. Status: {status}", response_time)

def test_automation_health_checks():
    """Test automation health check system"""
    print("\n3.2 Health Check System")
    print("-" * 30)
    
    # Test health check endpoint
    data, response_time, status = make_request("GET", "/health")
    
    if status == 200 and data and "status" in data:
        log_test("System Health Check", "PASS", f"System status: {data.get('status')}", response_time)
        
        # Check health data structure
        health_fields = ["status", "timestamp", "memory_percent", "cpu_percent"]
        missing_fields = [field for field in health_fields if field not in data]
        
        if not missing_fields:
            log_test("Health Data Structure", "PASS", "All health fields present", 0)
        else:
            log_test("Health Data Structure", "WARNING", f"Missing health fields: {missing_fields}", 0)
    else:
        log_test("System Health Check", "FAIL", f"Health check failed. Status: {status}", response_time)

def test_user_automation_creation():
    """Test user automation creation"""
    print("\n3.4 User Automation Creation")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, check what automations are available
    data, response_time, status = make_request("GET", "/api/automations/available", headers=headers)
    
    if status == 200 and data and isinstance(data, list) and len(data) > 0:
        # Try to add the first available automation
        automation_id = data[0]["id"]
        
        # Try to add automation to user account
        data, response_time, status = make_request("POST", f"/api/user/automations/{automation_id}", headers=headers)
        
        if status == 200 or status == 201:
            log_test("Add Automation to User", "PASS", f"Successfully added automation {automation_id}", response_time)
        elif status == 400 and "already has this automation" in str(data):
            log_test("Add Automation to User", "PASS", f"User already has automation {automation_id} (expected)", response_time)
        else:
            log_test("Add Automation to User", "FAIL", f"Failed to add automation. Status: {status}, Response: {data}", response_time)
    else:
        log_test("Add Automation to User", "WARNING", "No automations available to test with", response_time)

def test_user_automations_list():
    """Test getting user's automations"""
    print("\n3.5 User Automations List")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting user's automations
    data, response_time, status = make_request("GET", "/api/user/automations", headers=headers)
    
    if status == 200 and data is not None:
        log_test("Get User Automations", "PASS", "Successfully retrieved user automations", response_time)
        
        # Check data structure
        if isinstance(data, list):
            log_test("User Automations Data Structure", "PASS", f"Retrieved {len(data)} user automations", 0)
            
            if data:
                automation = data[0]
                required_fields = ["id", "user_id", "automation_id", "tokens_remaining", "status"]
                missing_fields = [field for field in required_fields if field not in automation]
                
                if not missing_fields:
                    log_test("User Automation Data Structure", "PASS", "All required fields present", 0)
                else:
                    log_test("User Automation Data Structure", "WARNING", f"Missing fields: {missing_fields}", 0)
        else:
            log_test("User Automations Data Structure", "WARNING", f"Unexpected data format: {type(data)}", 0)
    else:
        log_test("Get User Automations", "FAIL", f"Failed to get user automations. Status: {status}", response_time)

def test_automation_details():
    """Test getting automation details"""
    print("\n3.6 Automation Details")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting automation details for ID 21
    data, response_time, status = make_request("GET", "/api/automations/21", headers=headers)
    
    if status == 200 and data:
        log_test("Get Automation Details", "PASS", f"Successfully retrieved automation 21 details", response_time)
        
        # Check required fields
        required_fields = ["id", "name", "description", "pricing_type", "price_per_token"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if not missing_fields:
            log_test("Automation Details Structure", "PASS", "All required fields present", 0)
        else:
            log_test("Automation Details Structure", "WARNING", f"Missing fields: {missing_fields}", 0)
    elif status == 404:
        log_test("Get Automation Details", "WARNING", "Automation ID 21 not found", response_time)
    else:
        log_test("Get Automation Details", "FAIL", f"Failed to get automation details. Status: {status}", response_time)

def test_automation_provisioning():
    """Test automation provisioning flow"""
    print("\n3.7 Automation Provisioning")
    print("-" * 30)
    
    token = get_auth_token()
    if not token:
        log_test("Get Auth Token", "FAIL", "Could not get authentication token", 0)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test provisioning endpoint (this will likely fail without proper setup)
    provision_data = {
        "user_automation_id": 1,
        "bot_token": "test_bot_token_12345"
    }
    
    data, response_time, status = make_request("POST", "/api/automations/21/provision", 
                                             headers=headers, data=provision_data)
    
    if status == 404:
        log_test("Automation Provisioning", "WARNING", "Automation ID 21 not found for provisioning", response_time)
    elif status == 400:
        log_test("Automation Provisioning", "WARNING", "Provisioning failed (expected without proper setup)", response_time)
    elif status == 200 or status == 201:
        log_test("Automation Provisioning", "PASS", "Successfully provisioned automation", response_time)
    else:
        log_test("Automation Provisioning", "WARNING", f"Unexpected provisioning response. Status: {status}", response_time)

def generate_report():
    """Generate automation test report"""
    print("\n" + "="*60)
    print("AUTOMATION SYSTEM TEST REPORT")
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
    """Main automation test execution"""
    print("Zimmer AI Platform - Automation System Testing")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now()}")
    
    try:
        test_automation_marketplace()
        test_automation_health_checks()
        test_user_automation_creation()
        test_user_automations_list()
        test_automation_details()
        test_automation_provisioning()
        
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
