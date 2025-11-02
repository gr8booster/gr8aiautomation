# GR8 AI Automation - User Guide

## Overview

GR8 AI Automation is a production-ready SaaS platform that helps businesses automate workflows with AI-powered tools. The platform provides intelligent chatbots, lead capture forms, appointment scheduling, and more - all embeddable on any website with just a few lines of code.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Website Analysis](#website-analysis)
4. [Automations](#automations)
   - [AI Chatbot](#ai-chatbot)
   - [Lead Capture Forms](#lead-capture-forms)
   - [Appointment Scheduler](#appointment-scheduler)
5. [Dashboard](#dashboard)
6. [Analytics](#analytics)
7. [Billing & Plans](#billing--plans)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Quick Start (Demo Mode)

1. Visit the GR8 AI Automation homepage
2. Click **"Start Demo Now"** button (green button in hero section)
3. You'll be logged in with a Pro plan account and sample automations
4. Start exploring the dashboard immediately

### Production Login

1. Click **"Login with Google"** in the header
2. Authorize with your Google account
3. You'll start with a Free plan (upgrade available)

---

## Authentication

### Demo Login
- **Purpose**: Test the platform without OAuth setup
- **Plan**: Pro (full features)
- **Sample Data**: 2 pre-configured automations (chatbot + lead capture)
- **Limitations**: None - full Pro plan features

### Google OAuth Login
- **Purpose**: Production use with your own account
- **Initial Plan**: Free
- **Upgrade**: Available to Starter ($29/mo) or Pro ($99/mo)

### Session Management
- Sessions last 7 days
- Auto-logout on token expiry
- Secure httpOnly cookies for session storage

---

## Website Analysis

### How to Analyze a Website

1. **From Landing Page**:
   - Paste any URL in the input field
   - Click "Analyze Website"
   - Wait 10-30 seconds for AI analysis

2. **What You Get**:
   - Business type classification
   - 5-8 AI-powered automation recommendations
   - Each recommendation includes:
     - Title and description
     - Specific rationale for your website
     - Expected impact
     - Priority (High/Medium/Low)
     - Estimated value

3. **After Analysis**:
   - Click "Activate" on any recommendation
   - Automation is created and ready to use

### Supported Websites
- Any public website with HTML content
- E-commerce, SaaS, blogs, business websites
- Must be accessible via HTTP/HTTPS

---

## Automations

### AI Chatbot

**What It Does**: 24/7 intelligent customer support powered by GPT-4o-mini

**Setup Steps**:

1. **Activate Automation**:
   - Analyze your website
   - Click "Activate" on "AI Customer Support Agent"
   - Automation appears in dashboard

2. **Get Embed Code**:
   - Go to Dashboard
   - Find your chatbot automation
   - Click "Get Code" button
   - Copy the generated code

3. **Install on Your Website**:
   ```html
   <!-- Paste this before closing </body> tag -->
   <script src="https://your-domain.com/widget.js"></script>
   <script>
     GR8Chatbot.init({
       websiteId: 'your-website-id',
       apiUrl: 'https://your-backend-url.com/api'
     });
   </script>
   ```

4. **Test Widget**:
   - Click "Test" button in dashboard
   - Opens demo page with live chatbot
   - Try asking questions

**Features**:
- Context-aware responses based on your website content
- Session persistence (conversations saved)
- Mobile responsive design
- Customizable appearance (colors, position)
- Typing indicators
- 30 messages/minute rate limit

**Pricing Impact**:
- Free: 100 AI interactions/month
- Starter: 1,000 AI interactions/month
- Pro: 10,000 AI interactions/month

---

### Lead Capture Forms

**What It Does**: Smart forms with AI-powered auto-responses and lead scoring

**Setup Steps**:

1. **Create Form**:
   - Go to Lead Capture page
   - Click "Create Form"
   - Add fields (name, email, phone, message)
   - Enable auto-response

2. **Get Embed Code**:
   - Click "Get Code" on your form
   - Copy the generated code

3. **Install on Your Website**:
   ```html
   <div id="gr8-lead-form"></div>
   <script src="https://your-domain.com/lead-form-widget.js"></script>
   <script>
     GR8LeadForm.init({
       formId: 'your-form-id',
       apiUrl: 'https://your-backend-url.com/api'
     });
   </script>
   ```

**Features**:
- AI lead scoring (hot/warm/cold)
- Personalized auto-response emails (if SendGrid configured)
- Real-time validation
- Custom fields
- Mobile responsive
- 10 submissions/minute rate limit

**Lead Management**:
- View all leads in Lead Capture page
- See AI-assigned scores
- Filter by score
- View auto-response content
- Export leads (coming soon)

---

### Appointment Scheduler

**What It Does**: Automated appointment booking with calendar integration and email confirmations

**Setup Steps**:

1. **Configure Availability**:
   - Set business hours per day
   - Define appointment slot duration (default: 30 min)
   - Set buffer time between appointments (default: 15 min)

2. **Get Available Slots**:
   - API endpoint: `GET /api/appointments/availability?website_id={id}&date={date}`
   - Returns list of available time slots

3. **Book Appointment** (Public API):
   ```javascript
   fetch('/api/appointments/book', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       website_id: 'your-website-id',
       start_time: '2024-01-15T10:00:00Z',
       duration: 30,
       customer_name: 'John Doe',
       customer_email: 'john@example.com',
       customer_phone: '+1234567890',
       notes: 'Initial consultation'
     })
   });
   ```

4. **Confirmation Email**:
   - Automatically sent to customer (if SendGrid configured)
   - Includes date, time, duration
   - Formatted professional email

**Features**:
- Business hours management
- Conflict detection
- Email confirmations
- Appointment cancellation
- Calendar view (coming soon)
- Multiple timezones support

---

## Dashboard

### Overview

The Dashboard is your control center for managing all automations.

### Stats Cards
- **Active Automations**: Number of running automations
- **Total Automations**: All automations (active + paused)
- **Executions**: Total workflow executions

### Automation Management

**Actions Available**:
- **Test**: Opens demo page to test widget
- **Get Code**: Shows embed code with copy button
- **Pause/Resume**: Toggle automation status

### Execution History Tab
- View all workflow executions
- See execution states: pending/running/completed/failed
- Duration tracking
- Triggered by (manual/webhook/schedule)

---

## Analytics

### Dashboard Metrics

**Overview Cards**:
- Total Automations (active count)
- Executions (success rate %)
- Chatbot Messages (session count)
- Total Leads (hot leads count)

**Time-Series Chart**:
- Activity over time (executions, messages, leads)
- Selectable periods: 7/30/90 days
- Interactive line chart

**Chatbot Performance**:
- Total messages
- Unique sessions
- Average messages per session

**Lead Quality**:
- Total leads
- Hot leads count
- Conversion rate %

### Interpreting Data

- **High Messages/Session**: Users are engaged
- **High Hot Lead %**: Quality traffic
- **High Success Rate**: Automations working well

---

## Billing & Plans

### Plan Comparison

| Feature | Free | Starter ($29/mo) | Pro ($99/mo) |
|---------|------|------------------|--------------|
| Websites | 1 | 3 | 10 |
| Automations | 3 | 10 | Unlimited |
| AI Interactions/mo | 100 | 1,000 | 10,000 |
| Priority Support | ❌ | ✅ | ✅ |
| Advanced Analytics | ❌ | ✅ | ✅ |

### Upgrading Your Plan

1. Go to Billing page
2. Click "Upgrade" on desired plan
3. Complete Stripe checkout
4. Plan activates immediately

### Usage Tracking

- View current usage in Billing page
- Usage resets monthly
- Plan limits enforced automatically
- Friendly error messages when limits reached

---

## Troubleshooting

### Common Issues

#### Chatbot Not Responding

**Problem**: Widget loads but doesn't respond

**Solutions**:
1. Check website_id is correct
2. Verify automation is active (not paused)
3. Check browser console for errors
4. Ensure API URL is correct
5. Check rate limits (30 messages/minute)

#### Form Submissions Failing

**Problem**: Form submits but shows error

**Solutions**:
1. Check form_id is correct
2. Verify all required fields are filled
3. Check rate limits (10 submissions/minute)
4. Validate email format

#### Email Not Sending

**Problem**: Auto-response generated but email not received

**Solution**:
- SendGrid API key must be configured
- Email shows in lead record even if not sent
- Check SendGrid dashboard for delivery status

#### Authentication Issues

**Problem**: Session expired or 401 errors

**Solutions**:
1. Re-login (sessions last 7 days)
2. Clear cookies and re-authenticate
3. Check if JWT_SECRET_KEY changed

#### Rate Limit Errors

**Problem**: "Too many requests" error

**Solutions**:
- Wait 1 minute before retrying
- Rate limits: 5/min (analysis), 30/min (chatbot), 10/min (forms)
- Consider upgrading plan for higher limits (coming soon)

### Getting Help

**Demo Mode Issues**:
- Demo login always works with Pro plan
- Sample data auto-created
- No setup required

**Production Issues**:
1. Check application logs
2. Verify environment variables
3. Check MongoDB connection
4. Review Sentry error tracking (if configured)

**Contact Support**:
- In-app support chat (coming soon)
- Email: support@gr8ai.com
- Documentation: /docs

---

## Best Practices

### Security
- Never expose API keys in client-side code
- Use environment variables for secrets
- Validate webhook signatures (Stripe)
- Implement HTTPS only

### Performance
- Database indexes are optimized
- Rate limiting prevents abuse
- AI responses cached where appropriate
- Use CDN for widget scripts (recommended)

### User Experience
- Test automations before going live
- Monitor analytics regularly
- Respond to hot leads quickly
- Keep business hours updated

---

## API Reference

### Public Endpoints (No Auth Required)

```
POST /api/chatbot/message
POST /api/forms/{form_id}/submit
GET /api/appointments/availability
POST /api/appointments/book
```

### Protected Endpoints (Auth Required)

```
GET /api/auth/me
POST /api/analyze
GET /api/automations
POST /api/automations
GET /api/leads
GET /api/analytics/dashboard
```

### Rate Limits

- Analysis: 5 requests/minute
- Chatbot: 30 messages/minute
- Form submit: 10 submissions/minute

---

## Next Steps

1. **Complete Setup**: Configure SendGrid for email delivery
2. **Test Thoroughly**: Use Test buttons in dashboard
3. **Deploy Widgets**: Install on your website
4. **Monitor Performance**: Check analytics daily
5. **Optimize**: Adjust based on analytics insights

---

## Support

For additional help:
- Check FAQ section in Billing page
- Review API documentation
- Contact support team

**Powered by GR8 AI Automation** 🚀
