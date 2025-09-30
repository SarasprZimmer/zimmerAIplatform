#!/usr/bin/env python3
"""
Quick Automation Connection Test
===============================

This script quickly tests the automation connection system on the server.
It checks the current state and identifies immediate issues.

Usage:
    python3 quick_automation_test.py
"""

import os
import sys
import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "https://api.zimmerai.com"

async def quick_test():
    """Quick test of automation connection system"""
    print("🚀 Quick Automation Connection Test")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        issues = []
        
        # Test 1: Check marketplace automations
        print("1. Testing marketplace automations...")
        try:
            response = await client.get(f"{BASE_URL}/api/automations/marketplace")
            if response.status_code == 200:
                data = response.json()
                automations = data.get("automations", [])
                print(f"   ✅ Found {len(automations)} automations")
                
                for automation in automations:
                    print(f"   - {automation.get('name')} (ID: {automation.get('id')})")
                    print(f"     Status: {automation.get('status')}, Listed: {automation.get('is_listed')}")
                    print(f"     Health: {automation.get('health_status')}")
                    print(f"     Provision URL: {automation.get('api_provision_url')}")
                    
                    if not automation.get('api_provision_url'):
                        issues.append(f"Automation {automation.get('name')} missing provision URL")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                issues.append("Failed to fetch marketplace automations")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            issues.append("Marketplace automations endpoint error")
        
        # Test 2: Check database automations
        print("\n2. Testing database automations...")
        try:
            from sqlalchemy import create_engine, text
            from dotenv import load_dotenv
            load_dotenv()
            
            DATABASE_URL = os.getenv('DATABASE_URL')
            if not DATABASE_URL:
                print("   ❌ No DATABASE_URL found")
                issues.append("Missing DATABASE_URL environment variable")
            else:
                engine = create_engine(DATABASE_URL)
                with engine.begin() as conn:
                    result = conn.execute(text("SELECT id, name, status, is_listed, api_provision_url FROM automations"))
                    db_automations = result.fetchall()
                    
                    print(f"   ✅ Found {len(db_automations)} automations in database")
                    
                    for auto in db_automations:
                        print(f"   - {auto[1]} (ID: {auto[0]})")
                        print(f"     Status: {auto[2]}, Listed: {auto[3]}")
                        print(f"     Provision URL: {auto[4]}")
                        
                        if not auto[4]:
                            issues.append(f"Database automation {auto[1]} missing provision URL")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            issues.append("Database connection error")
        
        # Test 3: Check environment variables
        print("\n3. Testing environment variables...")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check for service tokens
            service_tokens = []
            for key, value in os.environ.items():
                if key.startswith('AUTOMATION_') and key.endswith('_SERVICE_TOKEN'):
                    automation_id = key.replace('AUTOMATION_', '').replace('_SERVICE_TOKEN', '')
                    service_tokens.append(automation_id)
                    print(f"   ✅ Found service token for automation {automation_id}")
            
            if not service_tokens:
                print("   ⚠️  No service tokens found")
                issues.append("No automation service tokens configured")
        except Exception as e:
            print(f"   ❌ Environment error: {e}")
            issues.append("Environment variables error")
        
        # Test 4: Check API endpoints
        print("\n4. Testing API endpoints...")
        endpoints_to_test = [
            "/api/automations/marketplace",
            "/api/automations/available",
            "/api/automations"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    print(f"   ✅ {endpoint} - OK")
                else:
                    print(f"   ❌ {endpoint} - {response.status_code}")
                    issues.append(f"Endpoint {endpoint} returned {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {e}")
                issues.append(f"Endpoint {endpoint} error: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        if issues:
            print(f"❌ Found {len(issues)} issues:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            
            print("\n🔧 Recommended fixes:")
            print("   1. Ensure all automations have provision URLs")
            print("   2. Configure service tokens for each automation")
            print("   3. Set is_listed=true for automations to appear in marketplace")
            print("   4. Check API endpoint implementations")
        else:
            print("✅ All tests passed! No issues found.")
        
        return issues

if __name__ == "__main__":
    asyncio.run(quick_test())
