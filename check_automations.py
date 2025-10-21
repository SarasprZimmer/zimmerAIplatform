#!/usr/bin/env python3
"""
Check what automations exist in the system
"""

import requests
import json

BASE_URL = "https://api.zimmerai.com"

# Use the test user we created
login_data = {
    "email": "testuser1761038526@example.com",
    "password": "TestPassword123!"
}

# Login to get token
response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== CHECKING AUTOMATIONS ===")
    
    # Check available automations
    response = requests.get(f"{BASE_URL}/api/automations/available", headers=headers)
    print(f"Available Automations Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Available Automations: {json.dumps(data, indent=2)}")
    else:
        print(f"Available Automations Error: {response.text}")
    
    # Check marketplace
    response = requests.get(f"{BASE_URL}/api/automations/marketplace", headers=headers)
    print(f"\nMarketplace Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Marketplace: {json.dumps(data, indent=2)}")
    else:
        print(f"Marketplace Error: {response.text}")
    
    # Check all automations (admin endpoint)
    response = requests.get(f"{BASE_URL}/api/admin/automations", headers=headers)
    print(f"\nAdmin Automations Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Admin Automations: {json.dumps(data, indent=2)}")
    else:
        print(f"Admin Automations Error: {response.text}")
        
else:
    print(f"Login failed: {response.status_code} - {response.text}")
