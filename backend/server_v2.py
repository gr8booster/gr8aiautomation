"""
GR8 AI Automation - Production Backend
Phases 3-6: Authentication, Automations, Billing, Analytics
"""
from fastapi import FastAPI, HTTPException, Request, Response, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import httpx
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.schemas import (
    AnalysisRequest, AnalysisResponse, AutomationActivateRequest,
    Website, AutomationTemplate, ActiveAutomation, Execution, AutomationStatus, ExecutionState
)
from analyzer.website_fetcher import fetch_and_extract_website
from analyzer.ai_analyzer import analyze_website_for_automations
from services.orchestrator import OrchestratorService
from utils.db_helpers import serialize_doc, serialize_docs
from auth.jwt_handler import create_access_token, verify_token
from auth.dependencies import get_current_user, get_current_user_optional
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
)

app = FastAPI(title="GR8 AI Automation API - Production")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client["gr8_automation"]

# Collections
users_collection = db["users"]
sessions_collection = db["sessions"]
websites_collection = db["websites"]
automation_templates_collection = db["automation_templates"]
active_automations_collection = db["active_automations"]
workflows_collection = db["workflows"]
executions_collection = db["executions"]
subscriptions_collection = db["subscriptions"]
usage_collection = db["usage"]
payment_transactions_collection = db["payment_transactions"]
chatbot_messages_collection = db["chatbot_messages"]
chatbot_sessions_collection = db["chatbot_sessions"]
forms_collection = db["forms"]
leads_collection = db["leads"]
analytics_collection = db["analytics"]

# Orchestrator
orchestrator = OrchestratorService(db)

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Plan limits
PLAN_LIMITS = {
    "free": {
        "websites": 1,
        "automations": 3,
        "ai_interactions": 100,
        "price": 0
    },
    "starter": {
        "websites": 3,
        "automations": 10,
        "ai_interactions": 1000,
        "price": 29.0
    },
    "pro": {
        "websites": 10,
        "automations": 9999,
        "ai_interactions": 10000,
        "price": 99.0
    }
}

# Stripe price IDs (replace with your actual Stripe price IDs)
STRIPE_PRICES = {
    "starter": "price_starter_monthly",  # Create in Stripe Dashboard
    "pro": "price_pro_monthly"  # Create in Stripe Dashboard
}


# ========== STARTUP ==========
@app.on_event("startup")
async def seed_data():
    """Seed templates and create indexes"""
    # Seed templates
    existing = await automation_templates_collection.count_documents({})
    if existing == 0:
        templates = [
            {
                "_id": "ai-chatbot",
                "key": "ai-chatbot",
                "name": "24/7 AI Customer Support Agent",
                "description": "Intelligent chatbot that answers FAQs, qualifies leads, and provides instant support.",
                "category": "agent",
                "workflow_json": {"trigger_type": "webhook", "actions": ["receive_message", "ai_generate_response", "send_reply"]},
                "version": 1,
                "functional": True
            },
            {
                "_id": "lead-capture",
                "key": "lead-capture",
                "name": "Smart Lead Capture Forms",
                "description": "Capture leads with AI-powered auto-responses and intelligent qualification.",
                "category": "lead_generation",
                "workflow_json": {"trigger_type": "webhook", "actions": ["capture_form_data", "store_lead", "generate_autoresponse"]},
                "version": 1,
                "functional": True
            },
            {
                "_id": "appointment-scheduler",
                "key": "appointment-scheduler",
                "name": "Automated Appointment Booking",
                "description": "Let customers book appointments directly with calendar integration and reminders.",
                "category": "booking",
                "workflow_json": {"trigger_type": "webhook", "actions": ["check_availability", "book_slot", "send_confirmation"]},
                "version": 1,
                "functional": False
            },
            {
                "_id": "email-sequences",
                "key": "email-sequences",
                "name": "Automated Email Marketing",
                "description": "Send personalized email campaigns and nurture sequences automatically.",
                "category": "marketing",
                "workflow_json": {"trigger_type": "schedule", "actions": ["generate_email", "personalize_content", "queue_send"]},
                "version": 1,
                "functional": False
            },
            {
                "_id": "content-scheduler",
                "key": "content-scheduler",
                "name": "Social Media Content Scheduler",
                "description": "Plan and schedule social media posts across platforms in advance.",
                "category": "social_media",
                "workflow_json": {"trigger_type": "schedule", "actions": ["prepare_content", "post_to_platforms", "track_engagement"]},
                "version": 1,
                "functional": False
            },
            {
                "_id": "analytics-dashboard",
                "key": "analytics-dashboard",
                "name": "Website Analytics & Insights",
                "description": "Track visitors, conversions, and engagement with AI-powered insights.",
                "category": "analytics",
                "workflow_json": {"trigger_type": "webhook", "actions": ["track_event", "analyze_patterns", "generate_insights"]},
                "version": 1,
                "functional": False
            },
            {
                "_id": "webhook-automation",
                "key": "webhook-automation",
                "name": "Webhook Integration Hub",
                "description": "Connect with external tools and trigger custom workflows via webhooks.",
                "category": "automation",
                "workflow_json": {"trigger_type": "webhook", "actions": ["receive_webhook", "transform_data", "trigger_action"]},
                "version": 1,
                "functional": False
            },
            {
                "_id": "content-generator",
                "key": "content-generator",
                "name": "AI Content Generator",
                "description": "Generate blog posts, product descriptions, and marketing copy with AI.",
                "category": "automation",
                "workflow_json": {"trigger_type": "manual", "actions": ["analyze_topic", "generate_content", "optimize_seo"]},
                "version": 1,
                "functional": False
            }
        ]
        await automation_templates_collection.insert_many(templates)
        print(f"✓ Seeded {len(templates)} automation templates")
    
    # Create indexes
    await users_collection.create_index("email", unique=True)
    await sessions_collection.create_index("expires_at")
    await active_automations_collection.create_index([("owner_id", 1), ("status", 1)])
    print("✓ Database indexes created")


# ========== HEALTH & INFO ==========
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "GR8 AI Automation - Production", "version": "2.0"}


# ========== AUTHENTICATION ==========
@app.post("/api/auth/session")
async def get_session_data(request: Request, response: Response):
    """
    Process Emergent Auth session_id and create user session
    """
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="X-Session-ID header required")
    
    # Call Emergent Auth to get session data
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            auth_response.raise_for_status()
            session_data = auth_response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to verify session: {str(e)}")
    
    # Extract user data
    user_id = session_data.get("id")
    email = session_data.get("email")
    name = session_data.get("name")
    picture = session_data.get("picture")
    emergent_session_token = session_data.get("session_token")
    
    # Check if user exists
    existing_user = await users_collection.find_one({"email": email})
    
    if not existing_user:
        # Create new user
        user_doc = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "picture": picture,
            "emergent_user_id": user_id,
            "plan": "free",
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        }
        await users_collection.insert_one(user_doc)
        
        # Create free subscription
        subscription_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_doc["_id"],
            "plan": "free",
            "status": "active",
            "current_period_start": datetime.now(timezone.utc),
            "current_period_end": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc)
        }
        await subscriptions_collection.insert_one(subscription_doc)
        
        user_data = user_doc
    else:
        # Update last login
        await users_collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        user_data = existing_user
    
    # Create our JWT session token
    token_data = {
        "user_id": user_data["_id"],
        "email": email,
        "name": name,
        "picture": picture
    }
    session_token = create_access_token(token_data)
    
    # Store session in database
    session_doc = {
        "_id": str(uuid.uuid4()),
        "user_id": user_data["_id"],
        "session_token": session_token,
        "emergent_session_token": emergent_session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc)
    }
    await sessions_collection.insert_one(session_doc)
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/"
    )
    
    return {
        "user": serialize_doc(user_data),
        "session_token": session_token
    }


@app.get("/api/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    user_doc = await users_collection.find_one({"_id": user["user_id"]})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription
    subscription = await subscriptions_collection.find_one({"user_id": user["user_id"], "status": "active"})
    
    return {
        "user": serialize_doc(user_doc),
        "subscription": serialize_doc(subscription) if subscription else None
    }


@app.post("/api/auth/logout")
async def logout(request: Request, response: Response, user: dict = Depends(get_current_user)):
    """Logout user and clear session"""
    session_token = request.cookies.get('session_token')
    if session_token:
        await sessions_collection.delete_one({"session_token": session_token})
    
    response.delete_cookie("session_token", path="/")
    return {"message": "Logged out successfully"}


# ========== WEBSITE ANALYSIS ==========
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_website(request: AnalysisRequest, user: dict = Depends(get_current_user)):
    """
    Analyze website and recommend automations (AUTH REQUIRED)
    """
    try:
        # Check usage limits
        user_id = user["user_id"]
        user_doc = await users_collection.find_one({"_id": user_id})
        plan = user_doc.get("plan", "free")
        
        website_count = await websites_collection.count_documents({"owner_id": user_id})
        if website_count >= PLAN_LIMITS[plan]["websites"]:
            raise HTTPException(
                status_code=403,
                detail=f"Website limit reached for {plan} plan. Upgrade to add more websites."
            )
        
        # Fetch and extract website
        extraction = await fetch_and_extract_website(request.url)
        
        # AI analysis
        analysis = await analyze_website_for_automations(extraction)
        
        # Store website
        website_id = str(uuid.uuid4())
        website = {
            "_id": website_id,
            "owner_id": user_id,
            "url": request.url,
            "title": extraction.title,
            "business_type": extraction.business_type.value,
            "fetched_at": datetime.now(timezone.utc),
            "analysis_summary": analysis.summary,
            "content_digest": extraction.content_text[:500]
        }
        await websites_collection.insert_one(website)
        
        # Track AI usage
        await track_usage(user_id, ai_interactions=1)
        
        # Format recommendations
        recommendations = [
            {
                "key": rec.key,
                "title": rec.title,
                "description": rec.description,
                "rationale": rec.rationale,
                "expected_impact": rec.expected_impact,
                "category": rec.category.value,
                "priority": rec.priority.value,
                "estimated_value": rec.estimated_value
            }
            for rec in analysis.recommendations
        ]
        
        return AnalysisResponse(
            analysis_id=website_id,
            url=request.url,
            summary=analysis.summary,
            business_type=analysis.business_type.value,
            strengths=analysis.strengths,
            opportunities=analysis.opportunities,
            recommendations=recommendations,
            confidence_score=analysis.confidence_score
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ========== AUTOMATIONS ==========
@app.get("/api/automations")
async def get_automations(user: dict = Depends(get_current_user)):
    """Get all active automations for user"""
    automations = await active_automations_collection.find({"owner_id": user["user_id"]}).to_list(length=100)
    return serialize_docs(automations)


@app.post("/api/automations")
async def activate_automation(request: AutomationActivateRequest, user: dict = Depends(get_current_user)):
    """Activate an automation"""
    try:
        user_id = user["user_id"]
        user_doc = await users_collection.find_one({"_id": user_id})
        plan = user_doc.get("plan", "free")
        
        # Check automation limit
        automation_count = await active_automations_collection.count_documents({"owner_id": user_id})
        if automation_count >= PLAN_LIMITS[plan]["automations"]:
            raise HTTPException(
                status_code=403,
                detail=f"Automation limit reached for {plan} plan. Upgrade to add more automations."
            )
        
        # Get website
        website = await websites_collection.find_one({"_id": request.website_id})
        if not website or website["owner_id"] != user_id:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Get template
        template = await automation_templates_collection.find_one({"key": request.recommendation_key})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create active automation
        automation_id = str(uuid.uuid4())
        automation = {
            "_id": automation_id,
            "owner_id": user_id,
            "website_id": request.website_id,
            "template_id": template["_id"],
            "name": template["name"],
            "status": "active",
            "config": request.config or {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await active_automations_collection.insert_one(automation)
        
        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = {
            "_id": workflow_id,
            "owner_id": user_id,
            "website_id": request.website_id,
            "automation_id": automation_id,
            "name": template["name"],
            "nodes": template.get("workflow_json", {}).get("actions", []),
            "edges": [],
            "variables": {},
            "version": 1,
            "created_at": datetime.now(timezone.utc)
        }
        await workflows_collection.insert_one(workflow)
        
        # Create initial execution
        execution_id = await orchestrator.create_execution(workflow_id, "activation")
        await orchestrator.add_log(execution_id, f"Automation '{template['name']}' activated")
        await orchestrator.update_execution_state(execution_id, "completed")
        
        return serialize_doc(automation)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")


# Continue with remaining endpoints...
