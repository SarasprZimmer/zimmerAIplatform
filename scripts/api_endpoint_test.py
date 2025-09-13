#!/usr/bin/env python3
"""
Comprehensive API Endpoint Test Script
Tests all endpoints on both admin and user panels against the backend
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EndpointTest:
    name: str
    method: str
    url: str
    expected_status: int
    description: str
    requires_auth: bool = False
    payload: Dict = None

class APIEndpointTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.csrf_token = None
        
    def test_endpoint(self, test: EndpointTest) -> Dict:
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{test.url}"
            headers = {'Content-Type': 'application/json'}

            # Attach CSRF token when required and available
            if test.method in ('POST', 'PUT', 'DELETE'):
                # If session has CSRF cookie and we have a token, include header
                if self.csrf_token and self.session.cookies.get('XSRF-TOKEN'):
                    headers['X-CSRF-Token'] = self.csrf_token
            
            if test.requires_auth:
                # For now, skip auth-required endpoints
                return {
                    'name': test.name,
                    'url': url,
                    'status': 'SKIPPED (Auth Required)',
                    'error': 'Authentication not implemented in test',
                    'success': False
                }
            
            if test.method == 'GET':
                response = self.session.get(url, headers=headers)
            elif test.method == 'POST':
                response = self.session.post(url, headers=headers, json=test.payload or {})
            elif test.method == 'PUT':
                response = self.session.put(url, headers=headers, json=test.payload or {})
            elif test.method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                return {
                    'name': test.name,
                    'url': url,
                    'status': 'ERROR',
                    'error': f'Unsupported method: {test.method}',
                    'success': False
                }
            
            # Capture CSRF token if requested via endpoint
            if test.url == '/api/auth/csrf' and response.ok:
                try:
                    data = response.json()
                    # The middleware returns the token as csrf_token
                    self.csrf_token = data.get('csrf_token')
                except Exception:
                    pass

            success = response.status_code == test.expected_status
            result = {
                'name': test.name,
                'url': url,
                'status': response.status_code,
                'expected': test.expected_status,
                'success': success,
                'response_time': response.elapsed.total_seconds(),
                'error': None if success else f'Expected {test.expected_status}, got {response.status_code}'
            }
            
            if not success and response.text:
                try:
                    error_detail = response.json()
                    result['error_detail'] = error_detail
                except:
                    result['error_detail'] = response.text[:200]
            
            return result
            
        except requests.exceptions.ConnectionError:
            return {
                'name': test.name,
                'url': url,
                'status': 'CONNECTION_ERROR',
                'error': 'Cannot connect to backend',
                'success': False
            }
        except Exception as e:
            return {
                'name': test.name,
                'url': url,
                'status': 'EXCEPTION',
                'error': str(e),
                'success': False
            }
    
    def get_all_endpoints(self) -> List[EndpointTest]:
        """Define all endpoints to test"""
        return [
            # Health/Status Endpoints
            EndpointTest("CORS Test", "GET", "/test-cors", 200, "Basic CORS test endpoint"),
            
            # Auth Endpoints (User Panel)
            EndpointTest("User Login", "POST", "/api/auth/login", 401, "User login endpoint", False, {"email": "test@example.com", "password": "test"}),
            EndpointTest("User Logout", "POST", "/api/auth/logout", 401, "User logout endpoint", True),
            EndpointTest("User Refresh Token", "POST", "/api/auth/refresh", 401, "User token refresh", True),
            EndpointTest("User CSRF Token", "GET", "/api/auth/csrf", 200, "CSRF token endpoint"),
            EndpointTest("User Profile", "GET", "/api/me", 401, "Get current user profile", True),
            
            # User Management Endpoints (Admin Panel)
            EndpointTest("Admin Users List", "GET", "/api/admin/users", 401, "List all users", True),
            EndpointTest("Admin User Details", "GET", "/api/admin/users/1", 401, "Get specific user", True),
            EndpointTest("Admin Update User", "PUT", "/api/admin/users/1", 401, "Update user", True, {"name": "Test User"}),
            EndpointTest("Admin Delete User", "DELETE", "/api/admin/users/1", 401, "Delete user", True),
            
            # Automation Endpoints (Admin Panel)
            EndpointTest("Admin Automations List", "GET", "/api/admin/automations", 401, "List all automations", True),
            EndpointTest("Admin Automation Details", "GET", "/api/admin/automations/1", 401, "Get specific automation", True),
            EndpointTest("Admin Update Automation", "PUT", "/api/admin/automations/1", 401, "Update automation", True, {"name": "Test Automation"}),
            
            # User Automation Endpoints (User Panel)
            EndpointTest("User Automations List", "GET", "/api/user/automations", 401, "List user automations", True),
            EndpointTest("User Automation Details", "GET", "/api/user/automations/1", 401, "Get user automation", True),
            EndpointTest("Available Automations", "GET", "/api/automations", 200, "List available automations"),
            
            # Payment Endpoints
            EndpointTest("User Payments", "GET", "/api/user/payments", 401, "Get user payments", True),
            EndpointTest("Payment Details", "GET", "/api/admin/payments/1", 401, "Get payment details", True),
            EndpointTest("Zarinpal Init", "POST", "/api/payments/zarinpal/init", 401, "Initialize Zarinpal payment (requires auth)", False, {"automation_id": 1, "tokens": 100, "return_path": "/payment/return"}),
            
            # Support Ticket Endpoints
            EndpointTest("User Tickets", "GET", "/api/tickets", 401, "Get user tickets", True),
            EndpointTest("Create Ticket", "POST", "/api/tickets", 401, "Create support ticket", True, {"subject": "Test", "message": "Test message"}),
            EndpointTest("Admin Tickets", "GET", "/api/admin/tickets", 401, "List all tickets", True),
            EndpointTest("Update Ticket", "PUT", "/api/admin/tickets/1", 401, "Update ticket", True, {"status": "resolved"}),
            
            # Knowledge Base Endpoints
            EndpointTest("Knowledge Base List", "GET", "/api/admin/knowledge", 401, "List knowledge bases", True),
            EndpointTest("Knowledge Base Details", "GET", "/api/admin/knowledge/1", 401, "Get knowledge base", True),
            EndpointTest("Update Knowledge Base", "PUT", "/api/admin/knowledge/1", 401, "Update knowledge base", True, {"title": "Test KB"}),
            
            # System Endpoints
            EndpointTest("System Status", "GET", "/api/admin/system/status", 401, "Get system status", True),
            EndpointTest("Usage Stats", "GET", "/api/admin/usage", 401, "Get usage statistics", True),
            EndpointTest("Backups List", "GET", "/api/admin/backups", 401, "List backups", True),
            EndpointTest("Create Backup", "POST", "/api/admin/backups", 401, "Create backup", True),
            
            # Token Management Endpoints
            EndpointTest("Token Balance", "GET", "/api/admin/tokens/balance/1", 401, "Get token balance", True),
            EndpointTest("Token Adjustment", "POST", "/api/admin/tokens/adjust", 401, "Adjust tokens", True, {"user_automation_id": 1, "delta_tokens": 100, "reason": "Test"}),
            EndpointTest("Token Adjustments List", "GET", "/api/admin/tokens/adjustments", 401, "List token adjustments", True),
            
            # Password Reset Endpoints
            EndpointTest("Forgot Password", "POST", "/api/forgot-password", 200, "Request password reset (CSRF-aware)", False, {"email": "test@example.com"}),
            EndpointTest("Reset Password", "POST", "/api/reset-password", 400, "Reset password with invalid token (CSRF-aware)", False, {"token": "invalid", "new_password": "newpass"}),
            EndpointTest("Change Password", "POST", "/api/user/change-password", 401, "Change password", True, {"current_password": "old", "new_password": "new"}),
            
            # Fallback Endpoints
            EndpointTest("Fallbacks List", "GET", "/api/admin/fallbacks", 401, "List fallbacks", True),
            EndpointTest("Fallback Details", "GET", "/api/admin/fallbacks/1", 401, "Get fallback", True),
            EndpointTest("Update Fallback", "PUT", "/api/admin/fallbacks/1", 401, "Update fallback", True, {"name": "Test Fallback"}),
        ]
    
    def run_all_tests(self) -> List[Dict]:
        """Run all endpoint tests"""
        print(f"🚀 Starting API endpoint tests against {self.base_url}")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        endpoints = self.get_all_endpoints()
        total = len(endpoints)
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"Testing {i}/{total}: {endpoint.name}")
            result = self.test_endpoint(endpoint)
            self.results.append(result)
            
            # Print result immediately
            if result['success']:
                print(f"  ✅ {result['status']} - {result['response_time']:.3f}s")
            else:
                print(f"  ❌ {result['status']} - {result['error']}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        if not self.results:
            return "No test results available"
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        failed = total - successful
        
        report = f"""
# API Endpoint Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backend URL: {self.base_url}

## Summary
- Total Endpoints Tested: {total}
- ✅ Successful: {successful}
- ❌ Failed: {failed}
- Success Rate: {(successful/total)*100:.1f}%

## Detailed Results
"""
        
        # Group by success/failure
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        
        if successful_results:
            report += "\n### ✅ Working Endpoints\n"
            for result in successful_results:
                report += f"- **{result['name']}** - {result['status']} ({result['response_time']:.3f}s)\n"
        
        if failed_results:
            report += "\n### ❌ Failed Endpoints\n"
            for result in failed_results:
                report += f"- **{result['name']}** - {result['status']}\n"
                if result['error']:
                    report += f"  - Error: {result['error']}\n"
                if 'error_detail' in result:
                    report += f"  - Details: {result['error_detail']}\n"
        
        return report
    
    def save_report(self, filename: str = None):
        """Save the test report to a file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"api_test_report_{timestamp}.md"
        
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {filename}")
        return filename

def main():
    """Main function to run the API tests"""
    print("🔍 Zimmer API Endpoint Test Suite")
    print("=" * 50)
    
    # Test against backend
    tester = APIEndpointTester("http://localhost:8000")
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate and display report
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        report = tester.generate_report()
        print(report)
        
        # Save report
        filename = tester.save_report()
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Review the detailed report: {filename}")
        print(f"2. Fix backend issues first (500 errors, missing endpoints)")
        print(f"3. Fix frontend API calls (wrong URLs, missing /api prefixes)")
        print(f"4. Test authentication flow")
        print(f"5. Re-run tests to verify fixes")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")

if __name__ == "__main__":
    main()
