#!/usr/bin/env python3
"""
GR8 AI Automation Backend API Testing
Tests all endpoints for Phase 2 MVP functionality
"""
import requests
import sys
import json
import time
from datetime import datetime

class GR8BackendTester:
    def __init__(self, base_url="https://smarthub-ai-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.analysis_id = None
        self.automation_id = None
        self.workflow_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=timeout)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    self.log(f"   Error: {error_detail}")
                except:
                    self.log(f"   Response: {response.text[:200]}")
                return False, {}
                
        except requests.exceptions.Timeout:
            self.log(f"❌ {name} - Request timed out after {timeout}s")
            return False, {}
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}
    
    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET", 
            "api/health",
            200
        )
        return success and response.get('status') == 'healthy'
    
    def test_website_analysis(self):
        """Test website analysis with real website"""
        test_urls = [
            "https://stripe.com",
            "https://shopify.com", 
            "https://example.com"
        ]
        
        for url in test_urls:
            self.log(f"Testing analysis with {url}")
            success, response = self.run_test(
                f"Website Analysis - {url}",
                "POST",
                "api/analyze", 
                200,
                data={"url": url},
                timeout=45  # AI analysis takes time
            )
            
            if success:
                # Validate response structure
                required_fields = ['analysis_id', 'url', 'summary', 'business_type', 'recommendations']
                if all(field in response for field in required_fields):
                    self.analysis_id = response['analysis_id']
                    self.log(f"   ✓ Analysis ID: {self.analysis_id}")
                    self.log(f"   ✓ Business Type: {response['business_type']}")
                    self.log(f"   ✓ Recommendations: {len(response['recommendations'])}")
                    return True
                else:
                    self.log(f"   ❌ Missing required fields in response")
                    return False
            else:
                # Try next URL if this one fails
                continue
                
        return False
    
    def test_get_automations(self):
        """Test getting automations list"""
        success, response = self.run_test(
            "Get Automations",
            "GET",
            "api/automations",
            200
        )
        
        if success:
            self.log(f"   ✓ Found {len(response)} automations")
            return True
        return False
    
    def test_activate_automation(self):
        """Test automation activation"""
        if not self.analysis_id:
            self.log("❌ Cannot test activation - no analysis_id available")
            return False
            
        # Test with a standard automation key
        success, response = self.run_test(
            "Activate Automation",
            "POST",
            "api/automations",
            200,
            data={
                "website_id": self.analysis_id,
                "recommendation_key": "ai-chatbot",
                "config": {}
            }
        )
        
        if success and '_id' in response:
            self.automation_id = response['_id']
            self.log(f"   ✓ Automation ID: {self.automation_id}")
            return True
        return False
    
    def test_get_automation_details(self):
        """Test getting specific automation details"""
        if not self.automation_id:
            self.log("❌ Cannot test automation details - no automation_id available")
            return False
            
        success, response = self.run_test(
            "Get Automation Details",
            "GET",
            f"api/automations/{self.automation_id}",
            200
        )
        
        if success:
            self.log(f"   ✓ Automation: {response.get('name', 'Unknown')}")
            self.log(f"   ✓ Status: {response.get('status', 'Unknown')}")
            return True
        return False
    
    def test_update_automation(self):
        """Test updating automation status"""
        if not self.automation_id:
            self.log("❌ Cannot test automation update - no automation_id available")
            return False
            
        success, response = self.run_test(
            "Update Automation Status",
            "PATCH",
            f"api/automations/{self.automation_id}",
            200,
            data={"status": "paused"}
        )
        
        if success and response.get('status') == 'paused':
            self.log(f"   ✓ Status updated to: paused")
            return True
        return False
    
    def test_get_executions(self):
        """Test getting execution history"""
        success, response = self.run_test(
            "Get Executions",
            "GET",
            "api/executions?limit=10",
            200
        )
        
        if success:
            self.log(f"   ✓ Found {len(response)} executions")
            return True
        return False
    
    def test_get_templates(self):
        """Test getting automation templates"""
        success, response = self.run_test(
            "Get Templates",
            "GET",
            "api/templates",
            200
        )
        
        if success:
            self.log(f"   ✓ Found {len(response)} templates")
            # Verify standard templates exist
            template_keys = [t.get('key') for t in response]
            expected_keys = ['ai-chatbot', 'lead-capture', 'appointment-scheduler']
            if all(key in template_keys for key in expected_keys):
                self.log(f"   ✓ All expected templates present")
                return True
            else:
                self.log(f"   ❌ Missing expected templates")
                return False
        return False
    
    def test_orchestrator_status(self):
        """Test orchestrator health"""
        success, response = self.run_test(
            "Orchestrator Status",
            "GET",
            "api/orchestrator/status",
            200
        )
        
        if success:
            self.log(f"   ✓ Queue depth: {response.get('queue_depth', 'Unknown')}")
            self.log(f"   ✓ Running: {response.get('running', 'Unknown')}")
            self.log(f"   ✓ Healthy: {response.get('healthy', 'Unknown')}")
            return True
        return False

def main():
    """Run all backend tests"""
    print("=" * 60)
    print("GR8 AI AUTOMATION - BACKEND API TESTING")
    print("=" * 60)
    
    tester = GR8BackendTester()
    
    # Core API Tests
    tests = [
        ("Health Check", tester.test_health_check),
        ("Templates", tester.test_get_templates),
        ("Website Analysis", tester.test_website_analysis),
        ("Get Automations", tester.test_get_automations),
        ("Activate Automation", tester.test_activate_automation),
        ("Get Automation Details", tester.test_get_automation_details),
        ("Update Automation", tester.test_update_automation),
        ("Get Executions", tester.test_get_executions),
        ("Orchestrator Status", tester.test_orchestrator_status),
    ]
    
    passed_tests = []
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests.append(test_name)
            else:
                failed_tests.append(test_name)
        except Exception as e:
            tester.log(f"❌ {test_name} - Exception: {str(e)}")
            failed_tests.append(test_name)
        
        print()  # Add spacing between tests
    
    # Results Summary
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed}")
    print(f"Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if passed_tests:
        print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
        for test in passed_tests:
            print(f"   • {test}")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test}")
    
    print("=" * 60)
    
    # Return exit code
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())