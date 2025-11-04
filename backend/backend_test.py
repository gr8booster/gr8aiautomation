"""
Comprehensive Backend API Testing for GR8 AI Automation
Tests all endpoints including auth, analysis, automations, chatbot, forms, appointments, analytics, and billing
"""
import requests
import sys
import time
from datetime import datetime, timedelta

class GR8BackendTester:
    def __init__(self, base_url="https://smarthub-ai-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failed_tests = []
        
        # Test data storage
        self.website_id = None
        self.automation_id = None
        self.form_id = None
        self.lead_id = None
        self.appointment_id = None

    def log(self, message, status="INFO"):
        """Log test messages"""
        symbols = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️", "WARN": "⚠️"}
        print(f"{symbols.get(status, 'ℹ️')} {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, cookies=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        # Add session token if available
        if self.session_token and not cookies:
            cookies = {'session_token': self.session_token}

        self.tests_run += 1
        self.log(f"Testing {name}...", "INFO")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, cookies=cookies, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, cookies=cookies, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, cookies=cookies, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"PASSED - {name} (Status: {response.status_code})", "PASS")
                try:
                    return True, response.json() if response.text else {}
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200] if response.text else "No response"
                })
                self.log(f"FAILED - {name} (Expected {expected_status}, got {response.status_code})", "FAIL")
                self.log(f"Response: {response.text[:200]}", "WARN")
                return False, {}

        except Exception as e:
            self.tests_failed += 1
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": str(e)
            })
            self.log(f"FAILED - {name} (Error: {str(e)})", "FAIL")
            return False, {}

    def test_health(self):
        """Test health endpoint"""
        self.log("\n=== TESTING HEALTH ENDPOINT ===", "INFO")
        success, data = self.run_test("Health Check", "GET", "/api/health", 200)
        return success

    def test_demo_login(self):
        """Test demo login"""
        self.log("\n=== TESTING AUTHENTICATION ===", "INFO")
        success, data = self.run_test("Demo Login", "POST", "/api/auth/demo", 200)
        
        if success and 'session_token' in data:
            self.session_token = data['session_token']
            self.user_id = data.get('user', {}).get('_id')
            self.log(f"Session token obtained: {self.session_token[:20]}...", "PASS")
            return True
        else:
            self.log("Failed to get session token from demo login", "FAIL")
            return False

    def test_get_me(self):
        """Test get current user"""
        success, data = self.run_test("Get Current User", "GET", "/api/auth/me", 200)
        if success:
            self.log(f"User plan: {data.get('user', {}).get('plan', 'unknown')}", "INFO")
        return success

    def test_templates(self):
        """Test get templates"""
        self.log("\n=== TESTING TEMPLATES ===", "INFO")
        success, data = self.run_test("Get Templates", "GET", "/api/templates", 200)
        if success:
            self.log(f"Found {len(data)} templates", "INFO")
        return success

    def test_website_analysis(self):
        """Test website analysis"""
        self.log("\n=== TESTING WEBSITE ANALYSIS ===", "INFO")
        success, data = self.run_test(
            "Analyze Website",
            "POST",
            "/api/analyze",
            200,
            data={"url": "https://example.com"}
        )
        
        if success and 'analysis_id' in data:
            self.website_id = data['analysis_id']
            self.log(f"Website analyzed, ID: {self.website_id}", "PASS")
            self.log(f"Business type: {data.get('business_type', 'unknown')}", "INFO")
            self.log(f"Recommendations: {len(data.get('recommendations', []))}", "INFO")
            return True
        return False

    def test_automations(self):
        """Test automation endpoints"""
        self.log("\n=== TESTING AUTOMATIONS ===", "INFO")
        
        # List automations
        success, data = self.run_test("List Automations", "GET", "/api/automations", 200)
        if success:
            self.log(f"Found {len(data)} automations", "INFO")
            if len(data) > 0:
                self.automation_id = data[0]['_id']
        
        # Activate automation (if we have a website_id)
        if self.website_id:
            success, data = self.run_test(
                "Activate Automation",
                "POST",
                "/api/automations",
                200,
                data={
                    "website_id": self.website_id,
                    "recommendation_key": "ai-chatbot",
                    "config": {}
                }
            )
            if success and '_id' in data:
                self.automation_id = data['_id']
                self.log(f"Automation activated, ID: {self.automation_id}", "PASS")
        
        # Update automation status (if we have an automation_id)
        if self.automation_id:
            success, data = self.run_test(
                "Update Automation Status",
                "PATCH",
                f"/api/automations/{self.automation_id}",
                200,
                data={"status": "paused"}
            )
        
        return True

    def test_chatbot(self):
        """Test chatbot endpoints"""
        self.log("\n=== TESTING CHATBOT ===", "INFO")
        
        # Test chatbot message (public endpoint, no auth required)
        session_id = f"test_session_{int(time.time())}"
        success, data = self.run_test(
            "Send Chatbot Message",
            "POST",
            "/api/chatbot/message",
            200,
            data={
                "website_id": "demo-website",
                "session_id": session_id,
                "message": "Hello, I need help with your services"
            },
            cookies=None  # Public endpoint
        )
        
        if success and 'response' in data:
            self.log(f"Chatbot response received: {data['response'][:50]}...", "PASS")
        
        # Test get chat history
        success, data = self.run_test(
            "Get Chat History",
            "GET",
            f"/api/chatbot/history/{session_id}",
            200,
            cookies=None  # Public endpoint
        )
        
        return True

    def test_forms_and_leads(self):
        """Test forms and lead capture"""
        self.log("\n=== TESTING FORMS & LEAD CAPTURE ===", "INFO")
        
        # Create form
        if self.website_id:
            success, data = self.run_test(
                "Create Form",
                "POST",
                "/api/forms",
                200,
                data={
                    "name": "Test Contact Form",
                    "website_id": self.website_id,
                    "fields": [
                        {"name": "name", "type": "text", "required": True},
                        {"name": "email", "type": "email", "required": True},
                        {"name": "message", "type": "textarea", "required": True}
                    ],
                    "settings": {"autoresponse_enabled": True}
                }
            )
            if success and '_id' in data:
                self.form_id = data['_id']
                self.log(f"Form created, ID: {self.form_id}", "PASS")
        
        # List forms
        success, data = self.run_test("List Forms", "GET", "/api/forms", 200)
        if success:
            self.log(f"Found {len(data)} forms", "INFO")
        
        # Submit form (public endpoint)
        form_id_to_use = self.form_id if self.form_id else "demo-form"
        success, data = self.run_test(
            "Submit Form",
            "POST",
            f"/api/forms/{form_id_to_use}/submit",
            200,
            data={
                "data": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "phone": "555-1234",
                    "message": "I'm interested in your services"
                }
            },
            cookies=None  # Public endpoint
        )
        
        if success:
            self.lead_id = data.get('lead_id')
            self.log(f"Form submitted, Lead ID: {self.lead_id}", "PASS")
            self.log(f"Lead score: {data.get('score', 'unknown')}", "INFO")
            self.log(f"Email sent: {data.get('email_sent', False)}", "INFO")
            if 'autoresponse' in data:
                self.log(f"Auto-response generated: {data['autoresponse'][:50]}...", "PASS")
        
        # List leads
        success, data = self.run_test("List Leads", "GET", "/api/leads", 200)
        if success:
            self.log(f"Found {len(data)} leads", "INFO")
        
        return True

    def test_appointments(self):
        """Test appointment scheduler"""
        self.log("\n=== TESTING APPOINTMENT SCHEDULER ===", "INFO")
        
        website_id = self.website_id if self.website_id else "demo-website"
        
        # Get availability
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        success, data = self.run_test(
            "Get Availability",
            "GET",
            f"/api/appointments/availability?website_id={website_id}&date={tomorrow}",
            200,
            cookies=None  # Public endpoint
        )
        
        if success:
            available_slots = data.get('available_slots', [])
            self.log(f"Found {len(available_slots)} available slots", "INFO")
            
            # Book appointment if slots available
            if len(available_slots) > 0:
                first_slot = available_slots[0]
                success, data = self.run_test(
                    "Book Appointment",
                    "POST",
                    "/api/appointments/book",
                    200,
                    data={
                        "website_id": website_id,
                        "start_time": first_slot['start_time'],
                        "duration": 30,
                        "customer_name": "Test Customer",
                        "customer_email": "customer@example.com",
                        "customer_phone": "555-9999",
                        "notes": "Test appointment"
                    },
                    cookies=None  # Public endpoint
                )
                
                if success and '_id' in data:
                    self.appointment_id = data['_id']
                    self.log(f"Appointment booked, ID: {self.appointment_id}", "PASS")
        
        # List appointments (requires auth)
        success, data = self.run_test("List Appointments", "GET", "/api/appointments", 200)
        if success:
            self.log(f"Found {len(data)} appointments", "INFO")
        
        return True

    def test_analytics(self):
        """Test analytics dashboard"""
        self.log("\n=== TESTING ANALYTICS ===", "INFO")
        
        for days in [7, 30, 90]:
            success, data = self.run_test(
                f"Get Analytics ({days} days)",
                "GET",
                f"/api/analytics/dashboard?days={days}",
                200
            )
            
            if success:
                overview = data.get('overview', {})
                self.log(f"Total automations: {overview.get('total_automations', 0)}", "INFO")
                self.log(f"Total executions: {overview.get('total_executions', 0)}", "INFO")
                self.log(f"Chatbot messages: {data.get('chatbot', {}).get('total_messages', 0)}", "INFO")
                self.log(f"Total leads: {data.get('leads', {}).get('total_leads', 0)}", "INFO")
                break  # Only test one period in detail
        
        return True

    def test_billing(self):
        """Test billing endpoints"""
        self.log("\n=== TESTING BILLING ===", "INFO")
        
        # Get plans
        success, data = self.run_test("Get Billing Plans", "GET", "/api/billing/plans", 200)
        if success:
            plans = data.get('plans', [])
            self.log(f"Found {len(plans)} billing plans", "INFO")
            for plan in plans:
                self.log(f"  - {plan.get('name')}: ${plan.get('price')}/mo", "INFO")
        
        # Note: Not testing checkout creation as it requires Stripe and would create actual sessions
        self.log("Skipping checkout creation test (would create real Stripe session)", "WARN")
        
        return True

    def test_executions(self):
        """Test execution history"""
        self.log("\n=== TESTING EXECUTIONS ===", "INFO")
        
        success, data = self.run_test("List Executions", "GET", "/api/executions", 200)
        if success:
            self.log(f"Found {len(data)} executions", "INFO")
        
        return True

    def test_content_generator(self):
        """Test AI Content Generator"""
        self.log("\n=== TESTING AI CONTENT GENERATOR ===", "INFO")
        
        # Get content templates
        success, data = self.run_test("Get Content Templates", "GET", "/api/content/templates", 200)
        if success:
            templates = data.get('templates', {})
            self.log(f"Found {len(templates)} content templates", "INFO")
        
        # Generate blog post
        success, data = self.run_test(
            "Generate Blog Post",
            "POST",
            "/api/content/generate",
            200,
            data={
                "content_type": "blog_post",
                "inputs": {
                    "topic": "Benefits of AI automation for small businesses",
                    "tone": "professional",
                    "length": "500",
                    "audience": "small business owners"
                }
            }
        )
        
        if success:
            if 'output' in data:
                self.log(f"Blog post generated: {len(data['output'])} characters", "PASS")
                self.log(f"Word count: {data.get('word_count', 0)}", "INFO")
            else:
                self.log("Blog post generation returned success but no output field", "FAIL")
                self.tests_failed += 1
                self.failed_tests.append({
                    "test": "Generate Blog Post - Output Validation",
                    "endpoint": "/api/content/generate",
                    "error": "Response missing 'output' field"
                })
        
        # Generate product description
        success, data = self.run_test(
            "Generate Product Description",
            "POST",
            "/api/content/generate",
            200,
            data={
                "content_type": "product_description",
                "inputs": {
                    "product_name": "Smart Home Assistant",
                    "product_details": "Voice-controlled AI device for home automation",
                    "audience": "tech-savvy homeowners",
                    "tone": "enthusiastic",
                    "length": "200"
                }
            }
        )
        
        if success and 'output' in data:
            self.log(f"Product description generated: {len(data['output'])} characters", "PASS")
        
        # Get content history
        success, data = self.run_test("Get Content History", "GET", "/api/content/history", 200)
        if success and data:
            self.log(f"Found {len(data)} content items in history", "INFO")
        
        return True

    def test_email_assistant(self):
        """Test AI Email Assistant"""
        self.log("\n=== TESTING AI EMAIL ASSISTANT ===", "INFO")
        
        # Draft email response
        success, data = self.run_test(
            "Draft Email Response",
            "POST",
            "/api/email/draft",
            200,
            data={
                "original_email": "Hi, I'm interested in your automation services. Can you tell me more about pricing and features?",
                "tone": "professional and friendly",
                "key_points": "Mention our Pro plan at $99/mo with unlimited automations",
                "recipient_name": "John"
            }
        )
        
        if success:
            if 'draft' in data:
                self.log(f"Email draft generated: {len(data['draft'])} characters", "PASS")
            else:
                self.log("Email draft returned success but no draft field", "FAIL")
                self.tests_failed += 1
                self.failed_tests.append({
                    "test": "Draft Email Response - Output Validation",
                    "endpoint": "/api/email/draft",
                    "error": "Response missing 'draft' field"
                })
        
        # Create email campaign
        success, data = self.run_test(
            "Create Email Campaign",
            "POST",
            "/api/email/campaign",
            200,
            data={
                "topic": "New AI Features Launch",
                "goal": "Drive signups for new features",
                "audience": "Existing customers",
                "tone": "exciting and professional",
                "num_variations": 2
            }
        )
        
        if success:
            if 'variations' in data:
                self.log(f"Email campaign generated with variations", "PASS")
        
        # Get email drafts history
        success, data = self.run_test("Get Email Drafts", "GET", "/api/email/drafts", 200)
        if success and data:
            self.log(f"Found {len(data)} email drafts in history", "INFO")
        
        return True

    def test_free_audit(self):
        """Test Free Audit Report Generation"""
        self.log("\n=== TESTING FREE AUDIT REPORT ===", "INFO")
        
        # Generate free report (public endpoint)
        success, data = self.run_test(
            "Generate Free Audit Report",
            "POST",
            "/api/reports/generate",
            200,
            data={
                "url": "https://example.com",
                "email": "test@example.com",
                "name": "Test User"
            },
            cookies=None  # Public endpoint
        )
        
        if success:
            self.log(f"Report ID: {data.get('report_id', 'N/A')}", "INFO")
            self.log(f"Lead score: {data.get('score', 'N/A')}", "INFO")
            self.log(f"Opportunities: {data.get('opportunities_count', 0)}", "INFO")
            self.log(f"Email sent: {data.get('email_sent', False)}", "INFO")
            
            if 'recommendations' in data:
                self.log(f"Recommendations preview: {len(data['recommendations'])} items", "PASS")
        
        # List reports (requires auth)
        success, data = self.run_test("List Reports", "GET", "/api/reports", 200)
        if success and data:
            self.log(f"Found {len(data)} reports", "INFO")
        
        # Test export CSV
        success, data = self.run_test("Export Reports CSV", "GET", "/api/reports/export", 200)
        if success:
            self.log("CSV export successful", "PASS")
        
        return True

    def test_workflow_builder(self):
        """Test Visual Workflow Builder"""
        self.log("\n=== TESTING WORKFLOW BUILDER ===", "INFO")
        
        # Save custom workflow
        success, data = self.run_test(
            "Save Custom Workflow",
            "POST",
            "/api/workflows/save",
            200,
            data={
                "name": "Test Workflow",
                "nodes": [
                    {"id": "1", "type": "trigger", "data": {"label": "Form Submit"}},
                    {"id": "2", "type": "action", "data": {"label": "Send Email"}}
                ],
                "edges": [
                    {"source": "1", "target": "2"}
                ]
            }
        )
        
        if success and 'workflow_id' in data:
            self.log(f"Workflow saved, ID: {data['workflow_id']}", "PASS")
        
        # List custom workflows
        success, data = self.run_test("List Custom Workflows", "GET", "/api/workflows/list", 200)
        if success:
            self.log(f"Found {len(data)} custom workflows", "INFO")
        
        return True

    def test_team_settings(self):
        """Test Team Collaboration"""
        self.log("\n=== TESTING TEAM SETTINGS ===", "INFO")
        
        # Get workspace
        success, data = self.run_test("Get Workspace", "GET", "/api/team/workspace", 200)
        if success:
            workspace = data.get('workspace', {})
            members = data.get('members', [])
            self.log(f"Workspace: {workspace.get('name', 'N/A')}", "INFO")
            self.log(f"Team members: {len(members)}", "INFO")
        
        # Invite team member
        success, data = self.run_test(
            "Invite Team Member",
            "POST",
            "/api/team/invite",
            200,
            data={
                "email": "newmember@example.com",
                "role": "member"
            }
        )
        
        if success and 'member_id' in data:
            self.log(f"Team member invited, ID: {data['member_id']}", "PASS")
        
        return True

    def test_settings_integrations(self):
        """Test Settings & Integrations"""
        self.log("\n=== TESTING SETTINGS & INTEGRATIONS ===", "INFO")
        
        # Get integration settings
        success, data = self.run_test("Get Integration Settings", "GET", "/api/settings/integrations", 200)
        if success:
            self.log(f"SendGrid configured: {data.get('sendgrid_configured', False)}", "INFO")
            self.log(f"Twilio configured: {data.get('twilio_configured', False)}", "INFO")
        
        return True

    def test_analytics_attribution(self):
        """Test Analytics Attribution"""
        self.log("\n=== TESTING ANALYTICS ATTRIBUTION ===", "INFO")
        
        success, data = self.run_test("Get Lead Attribution", "GET", "/api/analytics/attribution?days=30", 200)
        if success:
            self.log(f"Attribution data retrieved", "PASS")
        
        return True

    def run_all_tests(self):
        """Run all backend tests"""
        self.log("\n" + "="*60, "INFO")
        self.log("GR8 AI AUTOMATION - COMPREHENSIVE BACKEND API TESTING", "INFO")
        self.log("="*60 + "\n", "INFO")
        
        start_time = time.time()
        
        # Run tests in order
        self.test_health()
        
        # Auth is critical - if it fails, stop
        if not self.test_demo_login():
            self.log("\n❌ CRITICAL: Demo login failed. Cannot proceed with authenticated tests.", "FAIL")
            self.print_summary()
            return False
        
        self.test_get_me()
        self.test_templates()
        self.test_website_analysis()
        self.test_automations()
        self.test_chatbot()
        self.test_forms_and_leads()
        self.test_appointments()
        self.test_analytics()
        self.test_billing()
        self.test_executions()
        
        # NEW TESTS - Priority for this iteration
        self.log("\n" + "="*60, "INFO")
        self.log("TESTING NEW FEATURES (PRIORITY)", "INFO")
        self.log("="*60 + "\n", "INFO")
        
        self.test_content_generator()  # PRIORITY - Reported bug
        self.test_email_assistant()
        self.test_free_audit()
        self.test_workflow_builder()
        self.test_team_settings()
        self.test_settings_integrations()
        self.test_analytics_attribution()
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.print_summary(duration)
        
        # Return True if >50% tests passed
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        return success_rate > 50

    def print_summary(self, duration=0):
        """Print test summary"""
        self.log("\n" + "="*60, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*60, "INFO")
        self.log(f"Total Tests: {self.tests_run}", "INFO")
        self.log(f"Passed: {self.tests_passed} ✅", "PASS")
        self.log(f"Failed: {self.tests_failed} ❌", "FAIL")
        
        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            self.log(f"Success Rate: {success_rate:.1f}%", "INFO")
        
        if duration > 0:
            self.log(f"Duration: {duration:.2f}s", "INFO")
        
        if self.failed_tests:
            self.log("\n=== FAILED TESTS DETAILS ===", "FAIL")
            for failed in self.failed_tests:
                self.log(f"\nTest: {failed['test']}", "FAIL")
                self.log(f"Endpoint: {failed.get('endpoint', 'N/A')}", "INFO")
                if 'expected' in failed:
                    self.log(f"Expected: {failed['expected']}, Got: {failed['actual']}", "WARN")
                if 'error' in failed:
                    self.log(f"Error: {failed['error']}", "WARN")
                if 'response' in failed:
                    self.log(f"Response: {failed['response']}", "WARN")
        
        self.log("="*60 + "\n", "INFO")

def main():
    tester = GR8BackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
