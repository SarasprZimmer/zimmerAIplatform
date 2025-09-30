#!/usr/bin/env python3
"""
Comprehensive Automation Connection Test
========================================

This script tests the complete automation connection flow to identify all issues.
It simulates the user journey from marketplace to connection.

Test Flow:
1. Check available automations in marketplace
2. Create a mock automation (if needed)
3. Test user automation creation
4. Test automation provision/connection
5. Identify all errors and issues

Usage:
    python3 automation_connection_test.py
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
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class AutomationConnectionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.user_id = None
        self.test_automation_id = None
        self.test_user_automation_id = None
        
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

    async def test_authentication(self) -> bool:
        """Test user authentication"""
        self.log_info("Testing user authentication...")
        
        try:
            # Try to login
            response = await self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
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

    async def test_marketplace_automations(self) -> List[Dict]:
        """Test fetching available automations from marketplace"""
        self.log_info("Testing marketplace automations...")
        
        try:
            response = await self.session.get(
                f"{self.base_url}/api/automations/marketplace"
            )
            
            if response.status_code == 200:
                data = response.json()
                automations = data.get("automations", [])
                self.log_success(f"Found {len(automations)} automations in marketplace")
                
                for automation in automations:
                    self.log_info(f"  - {automation.get('name')} (ID: {automation.get('id')})")
                    self.log_info(f"    Status: {automation.get('status')}, Listed: {automation.get('is_listed')}")
                    self.log_info(f"    Health: {automation.get('health_status')}")
                    self.log_info(f"    Pricing: {automation.get('pricing_type')} - {automation.get('price_per_token')}")
                    self.log_info(f"    Provision URL: {automation.get('api_provision_url')}")
                
                return automations
            else:
                self.log_error(f"Failed to fetch marketplace automations: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_error("Marketplace automations test failed", e)
            return []

    async def test_user_automations(self) -> List[Dict]:
        """Test fetching user's automations"""
        self.log_info("Testing user automations...")
        
        if not self.access_token:
            self.log_error("No access token available")
            return []
        
        try:
            response = await self.session.get(
                f"{self.base_url}/api/user/automations",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                user_automations = data if isinstance(data, list) else data.get("items", [])
                self.log_success(f"Found {len(user_automations)} user automations")
                
                for ua in user_automations:
                    self.log_info(f"  - {ua.get('name')} (ID: {ua.get('id')})")
                    self.log_info(f"    Tokens: {ua.get('tokens_remaining')}, Demo: {ua.get('demo_tokens')}")
                    self.log_info(f"    Status: {ua.get('status')}, Integration: {ua.get('integration_status')}")
                
                return user_automations
            else:
                self.log_error(f"Failed to fetch user automations: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_error("User automations test failed", e)
            return []

    async def test_create_user_automation(self, automation_id: int) -> Optional[Dict]:
        """Test creating a user automation"""
        self.log_info(f"Testing user automation creation for automation {automation_id}...")
        
        if not self.access_token:
            self.log_error("No access token available")
            return None
        
        try:
            response = await self.session.post(
                f"{self.base_url}/api/user/automations/{automation_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"User automation created successfully")
                self.log_info(f"  User Automation ID: {data.get('id')}")
                self.log_info(f"  Tokens: {data.get('tokens_remaining')}")
                self.log_info(f"  Demo Tokens: {data.get('demo_tokens')}")
                self.test_user_automation_id = data.get('id')
                return data
            else:
                self.log_error(f"Failed to create user automation: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_error("User automation creation test failed", e)
            return None

    async def test_automation_provision(self, automation_id: int, user_automation_id: int, bot_token: str = None) -> bool:
        """Test automation provision/connection"""
        self.log_info(f"Testing automation provision for automation {automation_id}...")
        
        if not self.access_token:
            self.log_error("No access token available")
            return False
        
        try:
            provision_data = {
                "user_automation_id": user_automation_id,
                "bot_token": bot_token
            }
            
            response = await self.session.post(
                f"{self.base_url}/api/automations/{automation_id}/provision",
                json=provision_data,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"Automation provision successful")
                self.log_info(f"  Message: {data.get('message')}")
                self.log_info(f"  Success: {data.get('success')}")
                self.log_info(f"  Integration Status: {data.get('integration_status')}")
                return True
            else:
                self.log_error(f"Automation provision failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_error("Automation provision test failed", e)
            return False

    async def test_automation_health(self, automation_id: int) -> Dict:
        """Test automation health check"""
        self.log_info(f"Testing automation health for automation {automation_id}...")
        
        try:
            response = await self.session.get(
                f"{self.base_url}/api/automations/{automation_id}/health"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"Health check successful")
                self.log_info(f"  Status: {data.get('status')}")
                self.log_info(f"  Details: {data.get('details')}")
                return data
            else:
                self.log_error(f"Health check failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            self.log_error("Health check test failed", e)
            return {}

    async def create_mock_automation(self) -> Optional[Dict]:
        """Create a mock automation for testing (admin only)"""
        self.log_info("Creating mock automation for testing...")
        
        if not self.access_token:
            self.log_error("No access token available")
            return None
        
        mock_automation = {
            "name": "Test Automation Connection",
            "description": "Mock automation for testing connection flow",
            "pricing_type": "token_per_session",
            "price_per_token": 1000,
            "api_base_url": "https://mock-automation.example.com/api",
            "api_provision_url": "https://mock-automation.example.com/api/provision",
            "api_usage_url": "https://mock-automation.example.com/api/usage",
            "api_kb_status_url": "https://mock-automation.example.com/api/kb/status",
            "api_kb_reset_url": "https://mock-automation.example.com/api/kb/reset",
            "health_check_url": "https://mock-automation.example.com/api/health",
            "is_listed": True
        }
        
        try:
            response = await self.session.post(
                f"{self.base_url}/api/admin/automations",
                json=mock_automation,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_success(f"Mock automation created successfully")
                self.log_info(f"  Automation ID: {data.get('id')}")
                self.test_automation_id = data.get('id')
                return data
            else:
                self.log_error(f"Failed to create mock automation: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_error("Mock automation creation failed", e)
            return None

    async def run_comprehensive_test(self):
        """Run the complete automation connection test"""
        self.log_info("🚀 Starting Comprehensive Automation Connection Test")
        self.log_info("=" * 60)
        
        issues = []
        
        # Step 1: Authentication
        if not await self.test_authentication():
            issues.append("Authentication failed")
            return issues
        
        # Step 2: Check marketplace automations
        marketplace_automations = await self.test_marketplace_automations()
        if not marketplace_automations:
            issues.append("No automations available in marketplace")
            self.log_warning("Creating mock automation for testing...")
            mock_automation = await self.create_mock_automation()
            if not mock_automation:
                issues.append("Failed to create mock automation")
                return issues
            marketplace_automations = [mock_automation]
        
        # Step 3: Check user automations
        user_automations = await self.test_user_automations()
        
        # Step 4: Test automation connection flow
        for automation in marketplace_automations:
            automation_id = automation.get('id')
            automation_name = automation.get('name')
            
            self.log_info(f"Testing connection flow for: {automation_name}")
            
            # Check if user already has this automation
            user_has_automation = any(
                ua.get('automation_id') == automation_id 
                for ua in user_automations
            )
            
            if not user_has_automation:
                # Create user automation
                user_automation = await self.test_create_user_automation(automation_id)
                if not user_automation:
                    issues.append(f"Failed to create user automation for {automation_name}")
                    continue
                user_automation_id = user_automation.get('id')
            else:
                # Find existing user automation
                existing_ua = next(
                    ua for ua in user_automations 
                    if ua.get('automation_id') == automation_id
                )
                user_automation_id = existing_ua.get('id')
                self.log_info(f"Using existing user automation ID: {user_automation_id}")
            
            # Test health check
            health_data = await self.test_automation_health(automation_id)
            
            # Test provision (if automation has provision URL)
            if automation.get('api_provision_url'):
                provision_success = await self.test_automation_provision(
                    automation_id, 
                    user_automation_id,
                    bot_token="mock_bot_token_123456789"
                )
                if not provision_success:
                    issues.append(f"Failed to provision automation {automation_name}")
            else:
                self.log_warning(f"Automation {automation_name} has no provision URL")
                issues.append(f"Automation {automation_name} missing provision URL")
        
        # Summary
        self.log_info("=" * 60)
        self.log_info("🏁 Test Summary")
        
        if issues:
            self.log_error(f"Found {len(issues)} issues:")
            for i, issue in enumerate(issues, 1):
                self.log_error(f"  {i}. {issue}")
        else:
            self.log_success("All tests passed! No issues found.")
        
        return issues

async def main():
    """Main test function"""
    async with AutomationConnectionTester() as tester:
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
            print("3. Test with real automation URLs if available")
        else:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("The automation connection system is working correctly.")

if __name__ == "__main__":
    asyncio.run(main())
