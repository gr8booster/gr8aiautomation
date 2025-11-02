"""
GR8 AI Automation - Production Backend (Iteration 1)
Features: Authentication, AI Chatbot, Stripe Billing
"""
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import httpx
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

from models.schemas import (
    AnalysisRequest, AnalysisResponse, AutomationActivateRequest
)
from analyzer.website_fetcher import fetch_and_extract_website
from analyzer.ai_analyzer import analyze_website_for_automations
from services.orchestrator import OrchestratorService
from services.chatbot_service import process_chatbot_message, get_chatbot_history
from services.usage_tracker import PLAN_LIMITS, track_usage, get_usage, check_limit
from utils.db_helpers import serialize_doc, serialize_docs
from auth.jwt_handler import create_access_token
from auth.dependencies import get_current_user, get_current_user_optional
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest
)

app = FastAPI(title="GR8 AI Automation - Production")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URL = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(MONGO_URL)
db = client["gr8_automation"]

# Collections
users = db["users"]
sessions_db = db["sessions"]
websites = db["websites"]
templates = db["automation_templates"]
automations = db["active_automations"]
workflows = db["workflows"]
executions = db["executions"]
subscriptions = db["subscriptions"]
usage_db = db["usage"]
payments = db["payment_transactions"]
chatbot_messages = db["chatbot_messages"]
chatbot_sessions = db["chatbot_sessions"]

# Services
orchestrator = OrchestratorService(db)

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')


# ========== STARTUP ==========
@app.on_event("startup")
async def startup():
    """Seed data and create indexes"""
    # Seed templates
    count = await templates.count_documents({})
    if count == 0:
        template_list = [
            {"_id": "ai-chatbot", "key": "ai-chatbot", "name": "24/7 AI Customer Support Agent", "description": "Intelligent chatbot that answers FAQs, qualifies leads, and provides instant support.", "category": "agent", "functional": True, "version": 1},
            {"_id": "lead-capture", "key": "lead-capture", "name": "Smart Lead Capture Forms", "description": "Capture leads with AI-powered auto-responses.", "category": "lead_generation", "functional": False, "version": 1},
            {"_id": "appointment-scheduler", "key": "appointment-scheduler", "name": "Automated Appointment Booking", "description": "Let customers book appointments directly.", "category": "booking", "functional": False, "version": 1},
            {"_id": "email-sequences", "key": "email-sequences", "name": "Automated Email Marketing", "description": "Send personalized email campaigns automatically.", "category": "marketing", "functional": False, "version": 1},
            {"_id": "content-scheduler", "key": "content-scheduler", "name": "Social Media Content Scheduler", "description": "Plan and schedule social media posts.", "category": "social_media", "functional": False, "version": 1},
            {"_id": "analytics-dashboard", "key": "analytics-dashboard", "name": "Website Analytics & Insights", "description": "Track visitors, conversions, and engagement.", "category": "analytics", "functional": False, "version": 1},
        ]
        await templates.insert_many(template_list)
        print("✓ Seeded templates")
    
    # Indexes
    await users.create_index("email", unique=True)
    await sessions_db.create_index("expires_at")
    print("✓ Indexes created")


# ========== HEALTH ==========
@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0-iteration1"}


# ========== AUTH ==========
@app.post("/api/auth/session")
async def create_session(request: Request, response: Response):
    """Process Emergent Auth session"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(400, "X-Session-ID required")
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            r.raise_for_status()
            data = r.json()
        except:
            raise HTTPException(500, "Auth verification failed")
    
    email = data["email"]
    name = data["name"]
    picture = data.get("picture")
    
    # Get or create user
    user = await users.find_one({"email": email})
    if not user:
        user_id = str(uuid.uuid4())
        user = {
            "_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "plan": "free",
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        }
        await users.insert_one(user)
        
        # Create free subscription
        sub = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan": "free",
            "status": "active",
            "current_period_start": datetime.now(timezone.utc),
            "current_period_end": datetime.now(timezone.utc) + timedelta(days=365)
        }
        await subscriptions.insert_one(sub)
    else:
        await users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.now(timezone.utc)}})
    
    # Create JWT
    token = create_access_token({
        "user_id": user["_id"],
        "email": email,
        "name": name
    })
    
    # Store session
    await sessions_db.insert_one({
        "_id": str(uuid.uuid4()),
        "user_id": user["_id"],
        "session_token": token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc)
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    return {"user": serialize_doc(user), "session_token": token}


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user"""
    user_doc = await users.find_one({"_id": user["user_id"]})
    sub = await subscriptions.find_one({"user_id": user["user_id"], "status": "active"})
    usage = await get_usage(db, user["user_id"])
    
    return {
        "user": serialize_doc(user_doc),
        "subscription": serialize_doc(sub) if sub else None,
        "usage": usage,
        "limits": PLAN_LIMITS.get(user_doc.get("plan", "free"), PLAN_LIMITS["free"])
    }


@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """Logout"""
    token = request.cookies.get('session_token')
    if token:
        await sessions_db.delete_one({"session_token": token})
    response.delete_cookie("session_token", path="/")
    return {"message": "Logged out"}


@app.post("/api/auth/demo")
async def demo_login(response: Response):
    """Demo login for testing (creates test user)"""
    demo_email = "demo@gr8ai.com"
    
    # Get or create demo user
    user = await users.find_one({"email": demo_email})
    if not user:
        user_id = str(uuid.uuid4())
        user = {
            "_id": user_id,
            "email": demo_email,
            "name": "Demo User",
            "picture": None,
            "plan": "pro",  # Give demo user Pro plan for full testing
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        }
        await users.insert_one(user)
        
        # Create pro subscription for demo
        sub = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan": "pro",
            "status": "active",
            "current_period_start": datetime.now(timezone.utc),
            "current_period_end": datetime.now(timezone.utc) + timedelta(days=365)
        }
        await subscriptions.insert_one(sub)
    else:
        await users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.now(timezone.utc)}})
    
    # Create JWT
    token = create_access_token({
        "user_id": user["_id"],
        "email": demo_email,
        "name": "Demo User"
    })
    
    # Store session
    await sessions_db.insert_one({
        "_id": str(uuid.uuid4()),
        "user_id": user["_id"],
        "session_token": token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc)
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    return {"user": serialize_doc(user), "session_token": token, "message": "Demo login successful"}


# ========== ANALYSIS ==========
@app.post("/api/analyze")
async def analyze(req: AnalysisRequest, user: dict = Depends(get_current_user)):
    """Analyze website (AUTH REQUIRED)"""
    user_id = user["user_id"]
    user_doc = await users.find_one({"_id": user_id})
    plan = user_doc.get("plan", "free")
    
    # Check limits
    if not await check_limit(db, user_id, "websites", plan):
        raise HTTPException(403, f"Website limit reached. Upgrade your plan.")
    
    if not await check_limit(db, user_id, "ai_interactions", plan):
        raise HTTPException(403, f"AI interaction limit reached. Upgrade your plan.")
    
    try:
        extraction = await fetch_and_extract_website(req.url)
        analysis = await analyze_website_for_automations(extraction)
        
        website_id = str(uuid.uuid4())
        await websites.insert_one({
            "_id": website_id,
            "owner_id": user_id,
            "url": req.url,
            "title": extraction.title,
            "business_type": extraction.business_type.value,
            "fetched_at": datetime.now(timezone.utc),
            "analysis_summary": analysis.summary,
            "content_digest": extraction.content_text[:500]
        })
        
        await track_usage(db, user_id, ai_interactions=1)
        
        recommendations = [{
            "key": r.key,
            "title": r.title,
            "description": r.description,
            "rationale": r.rationale,
            "expected_impact": r.expected_impact,
            "category": r.category.value,
            "priority": r.priority.value,
            "estimated_value": r.estimated_value
        } for r in analysis.recommendations]
        
        return {
            "analysis_id": website_id,
            "url": req.url,
            "summary": analysis.summary,
            "business_type": analysis.business_type.value,
            "strengths": analysis.strengths,
            "opportunities": analysis.opportunities,
            "recommendations": recommendations,
            "confidence_score": analysis.confidence_score
        }
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


# ========== AUTOMATIONS ==========
@app.get("/api/automations")
async def list_automations(user: dict = Depends(get_current_user)):
    """List user's automations"""
    items = await automations.find({"owner_id": user["user_id"]}).to_list(100)
    return serialize_docs(items)


@app.post("/api/automations")
async def activate(req: AutomationActivateRequest, user: dict = Depends(get_current_user)):
    """Activate automation"""
    user_id = user["user_id"]
    user_doc = await users.find_one({"_id": user_id})
    plan = user_doc.get("plan", "free")
    
    if not await check_limit(db, user_id, "automations", plan):
        raise HTTPException(403, "Automation limit reached")
    
    website = await websites.find_one({"_id": req.website_id, "owner_id": user_id})
    if not website:
        raise HTTPException(404, "Website not found")
    
    template = await templates.find_one({"key": req.recommendation_key})
    if not template:
        raise HTTPException(404, "Template not found")
    
    auto_id = str(uuid.uuid4())
    await automations.insert_one({
        "_id": auto_id,
        "owner_id": user_id,
        "website_id": req.website_id,
        "template_id": template["_id"],
        "name": template["name"],
        "status": "active",
        "config": req.config or {},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    workflow_id = str(uuid.uuid4())
    await workflows.insert_one({
        "_id": workflow_id,
        "owner_id": user_id,
        "website_id": req.website_id,
        "automation_id": auto_id,
        "name": template["name"],
        "version": 1
    })
    
    exec_id = await orchestrator.create_execution(workflow_id, "activation")
    await orchestrator.add_log(exec_id, f"'{template['name']}' activated")
    await orchestrator.update_execution_state(exec_id, "completed")
    
    auto = await automations.find_one({"_id": auto_id})
    return serialize_doc(auto)


@app.patch("/api/automations/{automation_id}")
async def update_automation(automation_id: str, updates: dict, user: dict = Depends(get_current_user)):
    """Update automation"""
    result = await automations.update_one(
        {"_id": automation_id, "owner_id": user["user_id"]},
        {"$set": {**updates, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Not found")
    
    auto = await automations.find_one({"_id": automation_id})
    return serialize_doc(auto)


# ========== CHATBOT (PUBLIC) ==========
class ChatbotMessageRequest(BaseModel):
    website_id: str
    session_id: str
    message: str

@app.post("/api/chatbot/message")
async def chatbot_message(req: ChatbotMessageRequest):
    """Public chatbot endpoint (no auth required)"""
    website = await websites.find_one({"_id": req.website_id})
    if not website:
        raise HTTPException(404, "Website not found")
    
    # Check if chatbot automation is active
    chatbot_auto = await automations.find_one({
        "website_id": req.website_id,
        "template_id": "ai-chatbot",
        "status": "active"
    })
    if not chatbot_auto:
        raise HTTPException(403, "Chatbot not activated for this website")
    
    # Track usage for website owner
    await track_usage(db, website["owner_id"], chatbot_messages=1)
    
    # Process message
    result = await process_chatbot_message(db, req.website_id, req.session_id, req.message)
    return result


@app.get("/api/chatbot/history/{session_id}")


# ========== LEAD CAPTURE & FORMS ==========
from services.lead_service import generate_lead_autoresponse, score_lead

class FormSubmitRequest(BaseModel):
    data: dict

class FormCreateRequest(BaseModel):
    name: str
    website_id: str
    fields: List[dict]
    settings: Optional[dict] = None

@app.post("/api/forms")
async def create_form(req: FormCreateRequest, user: dict = Depends(get_current_user)):
    """Create a lead capture form"""
    form_id = str(uuid.uuid4())
    await db["forms"].insert_one({
        "_id": form_id,
        "owner_id": user["user_id"],
        "website_id": req.website_id,
        "name": req.name,
        "fields": req.fields,
        "settings": req.settings or {"autoresponse_enabled": True},
        "created_at": datetime.now(timezone.utc)
    })
    form = await db["forms"].find_one({"_id": form_id})
    return serialize_doc(form)

@app.get("/api/forms")
async def list_forms(user: dict = Depends(get_current_user)):
    """List user's forms"""
    items = await db["forms"].find({"owner_id": user["user_id"]}).to_list(100)
    return serialize_docs(items)

@app.post("/api/forms/{form_id}/submit")
async def submit_form(form_id: str, req: FormSubmitRequest):
    """PUBLIC endpoint for form submissions"""
    form = await db["forms"].find_one({"_id": form_id})
    if not form:
        raise HTTPException(404, "Form not found")
    
    # Score and store lead
    score = await score_lead(db, req.data)
    lead_id = str(uuid.uuid4())
    await db["leads"].insert_one({
        "_id": lead_id,
        "form_id": form_id,
        "website_id": form["website_id"],
        "owner_id": form["owner_id"],
        "data": req.data,
        "score": score,
        "status": "new",
        "created_at": datetime.now(timezone.utc)
    })
    
    # AI auto-response
    autoresponse = await generate_lead_autoresponse(db, req.data, form["website_id"])
    await db["leads"].update_one({"_id": lead_id}, {"$set": {"autoresponse_content": autoresponse}})
    await track_usage(db, form["owner_id"], ai_interactions=1)
    
    return {"success": True, "lead_id": lead_id, "autoresponse": autoresponse}

@app.get("/api/leads")
async def list_leads(user: dict = Depends(get_current_user)):
    """List leads"""
    items = await db["leads"].find({"owner_id": user["user_id"]}).sort("created_at", -1).limit(100).to_list(100)
    return serialize_docs(items)

# ========== ANALYTICS ==========
from services.analytics_service import get_dashboard_analytics

@app.get("/api/analytics/dashboard")
async def get_analytics(user: dict = Depends(get_current_user), days: int = 30):
    """Get dashboard analytics"""
    return await get_dashboard_analytics(db, user["user_id"], days)

async def chatbot_history(session_id: str):
    """Get chat history"""
    messages = await get_chatbot_history(db, session_id, limit=50)
    return serialize_docs(messages)


@app.get("/api/chatbot/widget/{website_id}")
async def get_widget_code(website_id: str):
    """Get embeddable widget code"""
    website = await websites.find_one({"_id": website_id})
    if not website:
        raise HTTPException(404, "Website not found")
    
    # Generate widget code
    widget_code = f"""<!-- GR8 AI Chatbot Widget -->
<script>
(function() {{
  const GR8_CONFIG = {{
    websiteId: '{website_id}',
    apiUrl: 'https://vibe-automation-1.preview.emergentagent.com/api'
  }};
  
  const script = document.createElement('script');
  script.src = GR8_CONFIG.apiUrl + '/widget.js';
  script.async = true;
  script.onload = function() {{
    GR8Chatbot.init(GR8_CONFIG);
  }};
  document.head.appendChild(script);
}})();
</script>"""
    
    return {"widget_code": widget_code, "website_id": website_id}


# ========== BILLING ==========
@app.get("/api/billing/plans")
async def get_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {"id": "free", "name": "Free", "price": 0, "features": PLAN_LIMITS["free"]},
            {"id": "starter", "name": "Starter", "price": 29, "features": PLAN_LIMITS["starter"]},
            {"id": "pro", "name": "Pro", "price": 99, "features": PLAN_LIMITS["pro"]}
        ]
    }


@app.post("/api/billing/checkout")
async def create_checkout(request: Request, plan_id: str, user: dict = Depends(get_current_user)):
    """Create Stripe checkout session"""
    if plan_id not in ["starter", "pro"]:
        raise HTTPException(400, "Invalid plan")
    
    # Get frontend origin for success/cancel URLs
    origin = request.headers.get("origin") or "https://vibe-automation-1.preview.emergentagent.com"
    
    # Initialize Stripe
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session
    amount = PLAN_LIMITS[plan_id]["price"]
    success_url = f"{origin}/billing/success?session_id={{{{CHECKOUT_SESSION_ID}}}}"
    cancel_url = f"{origin}/billing"
    
    checkout_req = CheckoutSessionRequest(
        amount=float(amount),
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "plan_id": plan_id,
            "type": "subscription"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_req)
    
    # Store pending transaction
    await payments.insert_one({
        "_id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "session_id": session.session_id,
        "plan_id": plan_id,
        "amount": amount,
        "currency": "usd",
        "status": "pending",
        "created_at": datetime.now(timezone.utc)
    })
    
    return {"url": session.url, "session_id": session.session_id}


@app.get("/api/billing/status/{session_id}")
async def check_payment_status(session_id: str, user: dict = Depends(get_current_user)):
    """Check payment status"""
    # Get transaction
    transaction = await payments.find_one({"session_id": session_id, "user_id": user["user_id"]})
    if not transaction:
        raise HTTPException(404, "Transaction not found")
    
    # If already processed, return status
    if transaction["status"] in ["completed", "failed"]:
        return serialize_doc(transaction)
    
    # Check with Stripe
    webhook_url = f"{str(Request.base_url)}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        status_response = await stripe_checkout.get_checkout_status(session_id)
        
        if status_response.payment_status == "paid" and transaction["status"] != "completed":
            # Update transaction
            await payments.update_one(
                {"_id": transaction["_id"]},
                {"$set": {"status": "completed", "payment_status": "paid", "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Upgrade user's plan
            plan_id = transaction["plan_id"]
            await users.update_one(
                {"_id": user["user_id"]},
                {"$set": {"plan": plan_id}}
            )
            
            # Update subscription
            await subscriptions.update_one(
                {"user_id": user["user_id"], "status": "active"},
                {"$set": {
                    "plan": plan_id,
                    "stripe_session_id": session_id,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            transaction["status"] = "completed"
        
        return serialize_doc(transaction)
    except Exception as e:
        print(f"Payment status check error: {e}")
        return serialize_doc(transaction)


@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    # Note: In production, validate webhook signature
    # For now, just return 200
    return {"received": True}


# ========== EXECUTIONS & TEMPLATES ==========
@app.get("/api/executions")
async def list_executions(workflow_id: str = None, user: dict = Depends(get_current_user)):
    """List execution history"""
    query = {"workflow_id": workflow_id} if workflow_id else {}
    items = await executions.find(query).sort("started_at", -1).limit(50).to_list(50)
    return serialize_docs(items)


@app.get("/api/templates")
async def list_templates():
    """List automation templates"""
    items = await templates.find().to_list(100)
    return serialize_docs(items)


@app.get("/api/orchestrator/status")
async def orchestrator_status():
    """Get orchestrator status"""
    return await orchestrator.get_queue_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
