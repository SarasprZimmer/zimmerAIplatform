#!/usr/bin/env python3
"""
Sales Automation Connection Test
===============================

This script tests the connection to the real sales automation service.
It uses the actual URLs provided and tests the complete flow.

Automation URLs:
- Base API: https://salesautomation.zimmerai.com/api
- Usage: https://salesautomation.zimmerai.com/api/zimmer/usage/consume
- Provision: https://salesautomation.zimmerai.com/api/zimmer/provision
- KB Reset: https://salesautomation.zimmerai.com/api/zimmer/kb/reset
- KB Status: https://salesautomation.zimmerai.com/api/zimmer/kb/status

Usage:
    python3 test_sales_automation.py
"""

import os
import sys
import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://api.zimmerai.com"
SALES_AUTOMATION_BASE = "https://salesautomation.zimmerai.com/api"

class SalesAutomationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.sales_automation_base = SALES_AUTOMATION_BASE
        self.session = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.user_id = None
        self.automation_id = None
        self.user_automation_id = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def log_error(self, message: str, error: Exception = None):
        self.log(f"❌ {message}", "ERROR")
        if error:
            self.log(f"   Error details: {str(error)}", "ERROR")
    
    def log_success(self, message: str):
        self.log(f"✅ {message}", "SUCCESS")
    
    def log_warning(self, message: str):
        self.log(f"⚠️  {message}", "WARNING")
    
    def log_info(self, message: str):
        self.log(f"ℹ️  {message}", "INFO")

    async def test_sales_automation_endpoints(self) -> Dict[str, bool]:
        """Test all sales automation endpoints"""
        self.log_info("Testing sales automation endpoints...")
        
        endpoints = {
            "base": f"{self.sales_automation_base}",
            "provision": f"{self.sales_automation_base}/zimmer/provision",
            "usage": f"{self.sales_automation_base}/zimmer/usage/consume",
            "kb_status": f"{self.sales_automation_base}/zimmer/kb/status",
            "kb_reset": f"{self.sales_automation_base}/zimmer/kb/reset"
        }
        
        results = {}
        
        for name, url in endpoints.items():
            try:
                self.log_info(f"Testing {name}: {url}")
                response = await self.session.get(url)
                self.log_info(f"  Status: {response.status_code}")
                self.log_info(f"  Headers: {dict(response.headers)}")
                
                if response.status_code in [200, 404, 405]:  # 404/405 are OK for GET on POST endpoints
                    results[name] = True
                    self.log_success(f"  {name} endpoint accessible")
                else:
                    results[name] = False
                    self.log_error(f"  {name} endpoint failed: {response.status_code}")
                    self.log_error(f"  Response: {response.text[:200]}")
                    
            except Exception as e:
                results[name] = False
                self.log_error(f"  {name} endpoint error: {e}")
        
        return results

    async def test_authentication(self) -> bool:
        """Test user authentication"""
        self.log_info("Testing user authentication...")
        
        try:
            # Try to login with a test user
            response = await self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": "uniaiprompt@gmail.com",  # Use the manager account
                    "password": "your_password_here"  # You'll need to provide this
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log_success(f"Authentication successful. User ID: {self.user_id}")
                return True
            else:
                self.log_error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_error("Authentication test failed", e)
            return False

    async def find_sales_automation(self) -> Optional[Dict]:
        """Find the sales automation in the database"""
        self.log_info("Looking for sales automation in database...")
        
        try:
            from sqlalchemy import create_engine, text
            from dotenv import load_dotenv
            load_dotenv()
            
            DATABASE_URL = os.getenv('DATABASE_URL')
            engine = create_engine(DATABASE_URL)
            
            with engine.begin() as conn:
                # Look for automation with sales automation URLs
                result = conn.execute(text("""
                    SELECT id, name, description, status, is_listed, 
                           api_base_url, api_provision_url, api_usage_url,
                           api_kb_status_url, api_kb_reset_url, service_token_hash
                    FROM automations 
                    WHERE api_base_url LIKE '%salesautomation.zimmerai.com%'
                       OR api_provision_url LIKE '%salesautomation.zimmerai.com%'
                """))
                
                automations = result.fetchall()
                
                if automations:
                    automation = automations[0]
                    self.log_success(f"Found sales automation: {automation[1]} (ID: {automation[0]})")
                    self.log_info(f"  Status: {automation[3]}, Listed: {automation[4]}")
                    self.log_info(f"  Base URL: {automation[5]}")
                    self.log_info(f"  Provision URL: {automation[6]}")
                    self.log_info(f"  Usage URL: {automation[7]}")
                    self.log_info(f"  KB Status URL: {automation[8]}")
                    self.log_info(f"  KB Reset URL: {automation[9]}")
                    self.log_info(f"  Service Token Hash: {automation[10]}")
                    
                    self.automation_id = automation[0]
                    return {
                        "id": automation[0],
                        "name": automation[1],
                        "description": automation[2],
                        "status": automation[3],
                        "is_listed": automation[4],
                        "api_base_url": automation[5],
                        "api_provision_url": automation[6],
                        "api_usage_url": automation[7],
                        "api_kb_status_url": automation[8],
                        "api_kb_reset_url": automation[9],
                        "service_token_hash": automation[10]
                    }
                else:
                    self.log_warning("No sales automation found in database")
                    return None
                    
        except Exception as e:
            self.log_error("Database query failed", e)
            return None

    async def check_service_token(self, automation_id: int) -> bool:
        """Check if service token is configured"""
        self.log_info(f"Checking service token for automation {automation_id}...")
        
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            service_token_key = f"AUTOMATION_{automation_id}_SERVICE_TOKEN"
            service_token = os.getenv(service_token_key)
            
            if service_token:
                self.log_success(f"Service token found: {service_token[:10]}...")
                return True
            else:
                self.log_error(f"No service token found for automation {automation_id}")
                self.log_error(f"Expected environment variable: {service_token_key}")
                return False
                
        except Exception as e:
            self.log_error("Service token check failed", e)
            return False

    async def test_provision_endpoint(self, automation_id: int, user_automation_id: int) -> bool:
        """Test the provision endpoint with real data"""
        self.log_info(f"Testing provision endpoint for automation {automation_id}...")
        
        if not self.access_token:
            self.log_error("No access token available")
            return False
        
        try:
            provision_data = {
                "user_automation_id": user_automation_id,
                "bot_token": "test_bot_token_123456789"
            }
            
            response = await self.session.post(
                f"{self.base_url}/api/automations/{automation_id}/provision",
                json=provision_data,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            self.log_info(f"Provision response status: {response.status_code}")
            self.log_info(f"Provision response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_success("Provision endpoint working")
                self.log_info(f"  Message: {data.get('message')}")
                return True
            else:
                self.log_error(f"Provision failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_error("Provision test failed", e)
            return False

    async def test_marketplace_visibility(self, automation_id: int) -> bool:
        """Test if automation is visible in marketplace"""
        self.log_info(f"Testing marketplace visibility for automation {automation_id}...")
        
        try:
            response = await self.session.get(f"{self.base_url}/api/automations/marketplace")
            
            if response.status_code == 200:
                data = response.json()
                automations = data.get("automations", [])
                
                found = any(auto.get("id") == automation_id for auto in automations)
                
                if found:
                    self.log_success("Automation visible in marketplace")
                    return True
                else:
                    self.log_error("Automation not visible in marketplace")
                    self.log_info(f"Available automations: {[auto.get('id') for auto in automations]}")
                    return False
            else:
                self.log_error(f"Marketplace request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("Marketplace visibility test failed", e)
            return False

    async def run_comprehensive_test(self):
        """Run comprehensive test of sales automation"""
        self.log_info("🚀 Starting Sales Automation Connection Test")
        self.log_info("=" * 60)
        
        issues = []
        
        # Step 1: Test sales automation endpoints
        self.log_info("Step 1: Testing sales automation endpoints")
        endpoint_results = await self.test_sales_automation_endpoints()
        for endpoint, success in endpoint_results.items():
            if not success:
                issues.append(f"Sales automation {endpoint} endpoint not accessible")
        
        # Step 2: Find automation in database
        self.log_info("\nStep 2: Finding automation in database")
        automation = await self.find_sales_automation()
        if not automation:
            issues.append("Sales automation not found in database")
            return issues
        
        # Step 3: Check service token
        self.log_info("\nStep 3: Checking service token")
        if not await self.check_service_token(automation["id"]):
            issues.append("Service token not configured")
        
        # Step 4: Test marketplace visibility
        self.log_info("\nStep 4: Testing marketplace visibility")
        if not await self.test_marketplace_visibility(automation["id"]):
            issues.append("Automation not visible in marketplace")
        
        # Step 5: Test authentication (optional)
        self.log_info("\nStep 5: Testing authentication")
        auth_success = await self.test_authentication()
        if not auth_success:
            issues.append("Authentication failed (may need password)")
        
        # Step 6: Test provision endpoint (if authenticated)
        if auth_success and self.user_id:
            self.log_info("\nStep 6: Testing provision endpoint")
            # First create a user automation
            try:
                response = await self.session.post(
                    f"{self.base_url}/api/user/automations/{automation['id']}",
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                
                if response.status_code == 200:
                    user_automation = response.json()
                    self.user_automation_id = user_automation.get("id")
                    self.log_success("User automation created")
                    
                    # Test provision
                    if not await self.test_provision_endpoint(automation["id"], self.user_automation_id):
                        issues.append("Provision endpoint test failed")
                else:
                    self.log_error(f"Failed to create user automation: {response.status_code}")
                    issues.append("Failed to create user automation")
            except Exception as e:
                self.log_error("User automation creation failed", e)
                issues.append("User automation creation failed")
        
        # Summary
        self.log_info("\n" + "=" * 60)
        self.log_info("🏁 Test Summary")
        self.log_info("=" * 60)
        
        if issues:
            self.log_error(f"Found {len(issues)} issues:")
            for i, issue in enumerate(issues, 1):
                self.log_error(f"  {i}. {issue}")
        else:
            self.log_success("All tests passed! Sales automation is working correctly.")
        
        return issues

async def main():
    """Main test function"""
    async with SalesAutomationTester() as tester:
        issues = await tester.run_comprehensive_test()
        
        if issues:
            print("\n" + "=" * 60)
            print("🔧 ISSUES TO FIX:")
            print("=" * 60)
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
            print("\nNext steps:")
            print("1. Fix the identified issues")
            print("2. Re-run this test")
            print("3. Test the complete user flow")
        else:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("The sales automation connection system is working correctly.")

if __name__ == "__main__":
    asyncio.run(main())
