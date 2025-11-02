# GR8 AI Automation - Technical Documentation

## Architecture Overview

### Tech Stack
- **Backend**: Python 3.11 + FastAPI + Motor (async MongoDB)
- **Frontend**: React 18 + TailwindCSS + shadcn/ui
- **Database**: MongoDB
- **AI**: OpenAI GPT-4o-mini via Emergent LLM
- **Email**: SendGrid
- **Payments**: Stripe
- **Error Tracking**: Sentry
- **Rate Limiting**: SlowAPI

### System Architecture

```
┌─────────────────┐
│   React SPA     │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (Port 8001)   │
├─────────────────┤
│  - Auth (JWT)   │
│  - Rate Limit   │
│  - Sentry       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ MongoDB │ │  External    │
│         │ │  - OpenAI    │
│         │ │  - SendGrid  │
│         │ │  - Stripe    │
└─────────┘ └──────────────┘
```

---

## Backend API

### Authentication

**JWT-based authentication with httpOnly cookies**

**Endpoints**:
- `POST /api/auth/demo` - Demo login (Pro plan)
- `POST /api/auth/session` - Google OAuth callback
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

**Token Structure**:
```python
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "exp": 1234567890
}
```

**JWT Secret**: Environment variable `JWT_SECRET_KEY`
**Expiry**: 7 days

---

### Core Services

#### 1. Chatbot Service (`services/chatbot_service.py`)

**Functions**:
- `process_chatbot_message(db, website_id, session_id, message)`
- `get_chatbot_history(db, session_id, limit=50)`

**AI Integration**:
```python
from emergentintegrations.llm.chat import LlmChat, UserMessage

chat = LlmChat(
    api_key=EMERGENT_LLM_KEY,
    session_id=f"chatbot-{session_id}",
    system_message=website_context
).with_model("openai", "gpt-4o-mini")

response = await chat.send_message(UserMessage(text=message))
```

**Data Flow**:
1. User sends message → stored in `chatbot_messages`
2. Get conversation history (last 10 messages)
3. Build context from website data
4. Call GPT-4o-mini with context
5. Store AI response → return to user

---

#### 2. Lead Service (`services/lead_service.py`)

**Functions**:
- `generate_lead_autoresponse(db, lead_data, website_id)`
- `score_lead(db, lead_data)` → returns "hot"/"warm"/"cold"
- `generate_and_send_lead_autoresponse(db, lead_data, website_id, send_email=True)`

**AI Lead Scoring**:
```python
# Criteria:
# HOT: Clear buying intent, specific requirements, urgent need
# WARM: Interested, some details provided, not urgent
# COLD: Generic inquiry, minimal info, unclear intent
```

**Email Integration**:
```python
from services.email_service import send_lead_autoresponse_email

email_sent = await send_lead_autoresponse_email(
    to_email=lead_email,
    lead_name=name,
    company_name=company,
    autoresponse_content=ai_response
)
```

---

#### 3. Appointment Scheduler (`services/appointment_service.py`)

**Class**: `AppointmentScheduler(db)`

**Key Methods**:
- `get_availability_settings(website_id)` - Get business hours
- `update_availability_settings(website_id, business_hours, ...)`
- `get_available_slots(website_id, date, duration)` - Calculate free slots
- `book_appointment(website_id, start_time, duration, customer_data)` - Book slot
- `cancel_appointment(appointment_id, reason)`

**Availability Algorithm**:
1. Get business hours for day of week
2. Generate time slots (default: 30 min slots)
3. Query existing appointments
4. Check for conflicts with buffer time (15 min)
5. Filter past slots
6. Return available slots

**Timezone Handling**: All datetimes stored in UTC

---

#### 4. Email Service (`services/email_service.py`)

**SendGrid Integration**:
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

async def send_email(to_email, subject, html_content, plain_text_content=None):
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    mail = Mail(
        from_email=Email(SENDER_EMAIL, SENDER_NAME),
        to_emails=To(to_email),
        subject=subject,
        html_content=Content("text/html", html_content)
    )
    response = await sg.send(mail)
    return response.status_code == 202
```

**Email Templates**:
- Lead auto-response: Personalized with AI-generated content
- Appointment confirmation: Professional HTML template

**Graceful Degradation**: If `SENDGRID_API_KEY` is empty, emails are not sent but auto-response content is still generated and stored.

---

#### 5. Usage Tracker (`services/usage_tracker.py`)

**Plan Limits**:
```python
PLAN_LIMITS = {
    "free": {
        "websites": 1,
        "automations": 3,
        "ai_interactions": 100
    },
    "starter": {
        "websites": 3,
        "automations": 10,
        "ai_interactions": 1000
    },
    "pro": {
        "websites": 10,
        "automations": 9999,
        "ai_interactions": 10000
    }
}
```

**Functions**:
- `track_usage(db, user_id, ai_interactions=0, chatbot_messages=0)`
- `get_usage(db, user_id)` - Get current month usage
- `check_limit(db, user_id, limit_type, plan)` - Returns True if within limit

**Monthly Aggregation**: Usage tracked per user per month (YYYY-MM format)

---

#### 6. Analytics Service (`services/analytics_service.py`)

**Metrics Calculated**:
- Total automations, active automations
- Total executions, success rate, failed executions
- Chatbot: messages, sessions, avg messages/session
- Leads: total, hot leads, conversion rate
- Time-series data (7-day default)

**Query Optimization**: Uses database indexes on timestamp fields for fast aggregation

---

### Database Schema

#### Collections

**users**:
```javascript
{
  _id: "uuid",
  email: "user@example.com",
  name: "User Name",
  picture: "url",
  plan: "free|starter|pro",
  created_at: ISODate,
  last_login: ISODate
}
```

**websites**:
```javascript
{
  _id: "uuid",
  owner_id: "user-uuid",
  url: "https://example.com",
  title: "Website Title",
  business_type: "saas|ecommerce|...",
  fetched_at: ISODate,
  analysis_summary: "AI analysis text",
  content_digest: "First 500 chars of content"
}
```

**active_automations**:
```javascript
{
  _id: "uuid",
  owner_id: "user-uuid",
  website_id: "website-uuid",
  template_id: "ai-chatbot|lead-capture|...",
  name: "Automation Name",
  status: "active|paused",
  config: {},
  created_at: ISODate,
  updated_at: ISODate
}
```

**chatbot_messages**:
```javascript
{
  _id: "uuid",
  website_id: "website-uuid",
  session_id: "session-uuid",
  role: "user|assistant",
  content: "Message text",
  timestamp: ISODate
}
```

**leads**:
```javascript
{
  _id: "uuid",
  form_id: "form-uuid",
  website_id: "website-uuid",
  owner_id: "user-uuid",
  data: {
    name: "Lead Name",
    email: "lead@example.com",
    phone: "+1234567890",
    message: "Lead message"
  },
  score: "hot|warm|cold",
  status: "new",
  autoresponse_content: "AI-generated response",
  autoresponse_email_sent: true,
  autoresponse_sent_at: ISODate,
  created_at: ISODate
}
```

**appointments**:
```javascript
{
  _id: "uuid",
  website_id: "website-uuid",
  start_time: ISODate,
  duration: 30,
  customer_name: "Customer Name",
  customer_email: "customer@example.com",
  customer_phone: "+1234567890",
  notes: "Appointment notes",
  status: "confirmed|cancelled",
  created_at: ISODate,
  confirmation_sent: true
}
```

#### Indexes

**Performance Optimized**:
```python
await users.create_index("email", unique=True)
await users.create_index("plan")
await sessions_db.create_index("expires_at")
await websites.create_index([("owner_id", 1), ("url", 1)])
await automations.create_index([("owner_id", 1), ("status", 1)])
await chatbot_messages.create_index([("website_id", 1), ("timestamp", -1)])
await leads.create_index([("owner_id", 1), ("created_at", -1)])
await appointments.create_index([("website_id", 1), ("start_time", 1)])
# ... and more
```

---

### Rate Limiting

**SlowAPI Configuration**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chatbot/message")
@limiter.limit("30/minute")
async def chatbot_message(request: Request, ...):
    ...
```

**Rate Limits**:
- Analysis: 5 requests/minute per IP
- Chatbot: 30 messages/minute per IP
- Form submission: 10 submissions/minute per IP

---

### Error Tracking

**Sentry Integration**:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

**Error Capture**: Automatic for all unhandled exceptions

---

## Frontend

### Component Structure

```
src/
├── App.js (Router setup)
├── contexts/
│   └── AuthContext.js (Global auth state)
├── components/
│   ├── ProtectedRoute.js (Auth wrapper)
│   └── ui/ (shadcn components)
├── pages/
│   ├── Landing.js (Home page)
│   ├── Dashboard.js (Automation management)
│   ├── Analytics.js (Metrics dashboard)
│   ├── Billing.js (Plans & upgrade)
│   ├── LeadCapture.js (Form management)
│   └── ...
└── index.css (Design tokens)
```

### Authentication Context

**AuthProvider**:
```javascript
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = () => {
    // Redirect to Google OAuth
  };

  const demoLogin = async () => {
    const response = await fetch(`${BACKEND_URL}/api/auth/demo`, {
      method: 'POST',
      credentials: 'include'
    });
    // ...
  };

  // Check session on mount
  useEffect(() => {
    checkSession();
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, demoLogin, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
```

---

### Embeddable Widgets

#### Chatbot Widget (`public/widget.js`)

**Vanilla JavaScript (350+ lines, zero dependencies)**

**Initialization**:
```javascript
window.GR8Chatbot = {
  init: function(config) {
    // config: { websiteId, apiUrl, position, theme, primaryColor }
    injectStyles();
    createWidget();
    attachEventListeners();
  }
};
```

**Features**:
- Floating chat button (bottom-right by default)
- Chat window with messages
- Typing indicators
- Session persistence (localStorage)
- Mobile responsive
- Inline CSS (no external dependencies)

**Usage**:
```html
<script src="https://your-domain.com/widget.js"></script>
<script>
  GR8Chatbot.init({
    websiteId: 'your-website-id',
    apiUrl: 'https://api.example.com'
  });
</script>
```

---

#### Lead Form Widget (`public/lead-form-widget.js`)

**Vanilla JavaScript (300+ lines, zero dependencies)**

**Initialization**:
```javascript
window.GR8LeadForm = {
  init: function(config) {
    // config: { formId, apiUrl }
    injectStyles();
    createForm();
    attachEventListeners();
  }
};
```

**Features**:
- Dynamic form rendering
- Real-time validation
- Success message with auto-response
- Mobile responsive
- Inline CSS

**Usage**:
```html
<div id="gr8-lead-form"></div>
<script src="https://your-domain.com/lead-form-widget.js"></script>
<script>
  GR8LeadForm.init({
    formId: 'your-form-id',
    apiUrl: 'https://api.example.com'
  });
</script>
```

---

## Deployment

### Environment Variables

**Backend (.env)**:
```bash
MONGO_URL=mongodb://localhost:27017
JWT_SECRET_KEY=your-secret-key-change-in-production
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
EMERGENT_LLM_KEY=sk-emergent-...
SENDGRID_API_KEY=SG....
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=Your Company Name
SENTRY_DSN=https://...@sentry.io/...
ENVIRONMENT=production
```

**Frontend (.env)**:
```bash
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

### Build & Run

**Backend**:
```bash
cd backend
pip install -r requirements.txt
python server.py
# Runs on 0.0.0.0:8001
```

**Frontend**:
```bash
cd frontend
yarn install
yarn build  # Production build
yarn start  # Development
# Runs on 0.0.0.0:3000
```

### Database Setup

1. Install MongoDB
2. Create database: `gr8_automation`
3. Collections auto-created on first use
4. Indexes created on startup

### Production Checklist

- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure Stripe webhook secret
- [ ] Add SendGrid API key
- [ ] Set Sentry DSN
- [ ] Configure CORS for your domain
- [ ] Enable HTTPS
- [ ] Set up MongoDB backups
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Test all integrations
- [ ] Load test with anticipated traffic
- [ ] Review security settings

---

## Testing

### Unit Tests

**Backend Tests** (`/app/backend/tests/`):
```bash
cd backend
pytest tests/ -v
```

**Test Coverage**:
- Chatbot service: 5 tests (4 passed)
- Lead service: 11 tests (11 passed)
- Usage tracker: 12 tests (12 passed)
- **Total**: 28 tests, 26 passed (93%)

### E2E Tests

**Testing Agent Report**: `/app/test_reports/iteration_2.json`

**Results**:
- Backend: 95% pass rate (19/20 tests)
- Frontend: 90% core features working
- Overall: 85% pass rate

---

## Security

### Authentication
- JWT tokens with httpOnly cookies
- 7-day token expiry
- Secure cookies (SameSite=None, Secure)
- OAuth integration (Google)

### API Security
- Rate limiting (SlowAPI)
- CORS configured
- Input validation (Pydantic)
- SQL injection prevention (NoSQL)
- XSS prevention (React escaping)

### Stripe Webhook Validation
```python
event = stripe.Webhook.construct_event(
    payload=body,
    sig_header=signature,
    secret=STRIPE_WEBHOOK_SECRET
)
```

### Data Protection
- Passwords not stored (OAuth only)
- API keys in environment variables
- Database credentials secured
- Session tokens encrypted (JWT)

---

## Performance

### Database Optimization
- 20+ indexes on critical fields
- Compound indexes for complex queries
- Query optimization via indexes

### Caching Strategy
- Session data cached in memory
- Static assets served with CDN (recommended)
- AI responses can be cached (future)

### Monitoring
- Sentry for error tracking
- Custom analytics for usage
- Response time tracking (future)

---

## API Changelog

### v2.0 (Current)
- ✅ Complete authentication system
- ✅ AI chatbot with GPT-4o-mini
- ✅ Lead capture with AI scoring
- ✅ Appointment scheduler
- ✅ SendGrid email integration
- ✅ Stripe billing
- ✅ Analytics dashboard
- ✅ Rate limiting
- ✅ Error tracking
- ✅ Database indexes

### v1.0 (POC)
- Basic website analysis
- Template system
- Mock automations

---

## Troubleshooting

### Common Issues

**MongoDB Connection Error**:
```
Solution: Check MONGO_URL in .env
Verify MongoDB is running: sudo systemctl status mongodb
```

**JWT Decode Error**:
```
Solution: JWT_SECRET_KEY changed, all sessions invalidated
Users must re-login
```

**Sentry Not Tracking**:
```
Solution: Check SENTRY_DSN is set
Verify Sentry project is active
```

**Email Not Sending**:
```
Solution: Check SENDGRID_API_KEY is set
Verify sender email is verified in SendGrid
Check SendGrid dashboard for errors
```

**Rate Limit Errors**:
```
Solution: Wait 1 minute before retrying
Check if IP is rate limited
Consider implementing user-specific rate limits
```

---

## Future Enhancements

### Planned Features
- [ ] Visual workflow builder
- [ ] Marketplace for templates
- [ ] Team collaboration
- [ ] Advanced analytics export
- [ ] SMS notifications (Twilio)
- [ ] Social media integrations
- [ ] Webhook automation
- [ ] Custom AI training
- [ ] Multi-language support
- [ ] White-label solution

### Performance Improvements
- [ ] Redis caching layer
- [ ] Background job queue (Celery)
- [ ] Database sharding
- [ ] CDN integration
- [ ] Response compression

### Security Enhancements
- [ ] 2FA authentication
- [ ] API key rotation
- [ ] Audit logging
- [ ] GDPR compliance tools
- [ ] SOC 2 certification

---

## Support & Resources

**Documentation**: `/app/USER_GUIDE.md`
**API Tests**: `/app/backend/tests/`
**Test Reports**: `/app/test_reports/`
**GitHub**: (Add your repo URL)
**Support Email**: support@gr8ai.com

---

**Version**: 2.0  
**Last Updated**: 2024-01-14  
**Maintained By**: GR8 AI Automation Team
