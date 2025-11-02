"""
GR8 AI Automation - FastAPI Backend
Launch-ready MVP with website analysis and automation orchestration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

from models.schemas import (
    AnalysisRequest, AnalysisResponse, AutomationActivateRequest,
    Website, AutomationTemplate, ActiveAutomation, Execution, AutomationStatus, ExecutionState
)
from analyzer.website_fetcher import fetch_and_extract_website
from analyzer.ai_analyzer import analyze_website_for_automations
from services.orchestrator import OrchestratorService
from utils.db_helpers import serialize_doc, serialize_docs

app = FastAPI(title="GR8 AI Automation API")

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
websites_collection = db["websites"]
automation_templates_collection = db["automation_templates"]
active_automations_collection = db["active_automations"]
workflows_collection = db["workflows"]
executions_collection = db["executions"]

# Orchestrator
orchestrator = OrchestratorService(db)

# Seed automation templates on startup
@app.on_event("startup")
async def seed_templates():
    """Seed automation templates"""
    existing = await automation_templates_collection.count_documents({})
    if existing > 0:
        return
    
    templates = [
        {
            "_id": "ai-chatbot",
            "key": "ai-chatbot",
            "name": "24/7 AI Customer Support Agent",
            "description": "Intelligent chatbot that answers FAQs, qualifies leads, and provides instant support.",
            "category": "agent",
            "workflow_json": {"trigger_type": "webhook", "actions": ["receive_message", "ai_generate_response", "send_reply"]},
            "version": 1
        },
        {
            "_id": "lead-capture",
            "key": "lead-capture",
            "name": "Smart Lead Capture Forms",
            "description": "Capture leads with AI-powered auto-responses and intelligent qualification.",
            "category": "lead_generation",
            "workflow_json": {"trigger_type": "webhook", "actions": ["capture_form_data", "store_lead", "generate_autoresponse"]},
            "version": 1
        },
        {
            "_id": "appointment-scheduler",
            "key": "appointment-scheduler",
            "name": "Automated Appointment Booking",
            "description": "Let customers book appointments directly with calendar integration and reminders.",
            "category": "booking",
            "workflow_json": {"trigger_type": "webhook", "actions": ["check_availability", "book_slot", "send_confirmation"]},
            "version": 1
        },
        {
            "_id": "email-sequences",
            "key": "email-sequences",
            "name": "Automated Email Marketing",
            "description": "Send personalized email campaigns and nurture sequences automatically.",
            "category": "marketing",
            "workflow_json": {"trigger_type": "schedule", "actions": ["generate_email", "personalize_content", "queue_send"]},
            "version": 1
        },
        {
            "_id": "content-scheduler",
            "key": "content-scheduler",
            "name": "Social Media Content Scheduler",
            "description": "Plan and schedule social media posts across platforms in advance.",
            "category": "social_media",
            "workflow_json": {"trigger_type": "schedule", "actions": ["prepare_content", "post_to_platforms", "track_engagement"]},
            "version": 1
        },
        {
            "_id": "analytics-dashboard",
            "key": "analytics-dashboard",
            "name": "Website Analytics & Insights",
            "description": "Track visitors, conversions, and engagement with AI-powered insights.",
            "category": "analytics",
            "workflow_json": {"trigger_type": "webhook", "actions": ["track_event", "analyze_patterns", "generate_insights"]},
            "version": 1
        },
        {
            "_id": "webhook-automation",
            "key": "webhook-automation",
            "name": "Webhook Integration Hub",
            "description": "Connect with external tools and trigger custom workflows via webhooks.",
            "category": "automation",
            "workflow_json": {"trigger_type": "webhook", "actions": ["receive_webhook", "transform_data", "trigger_action"]},
            "version": 1
        },
        {
            "_id": "content-generator",
            "key": "content-generator",
            "name": "AI Content Generator",
            "description": "Generate blog posts, product descriptions, and marketing copy with AI.",
            "category": "automation",
            "workflow_json": {"trigger_type": "manual", "actions": ["analyze_topic", "generate_content", "optimize_seo"]},
            "version": 1
        }
    ]
    
    await automation_templates_collection.insert_many(templates)
    print(f"✓ Seeded {len(templates)} automation templates")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "GR8 AI Automation"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_website(request: AnalysisRequest):
    """
    Analyze website and recommend automations
    """
    try:
        # Fetch and extract website
        extraction = await fetch_and_extract_website(request.url)
        
        # AI analysis
        analysis = await analyze_website_for_automations(extraction)
        
        # Store website
        website_id = str(uuid.uuid4())
        website = {
            "_id": website_id,
            "owner_id": "anonymous",
            "url": request.url,
            "title": extraction.title,
            "business_type": extraction.business_type.value,
            "fetched_at": datetime.now(timezone.utc),
            "analysis_summary": analysis.summary,
            "content_digest": extraction.content_text[:500]
        }
        await websites_collection.insert_one(website)
        
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


@app.get("/api/automations")
async def get_automations():
    """
    Get all active automations
    """
    automations = await active_automations_collection.find().to_list(length=100)
    return serialize_docs(automations)


@app.post("/api/automations")
async def activate_automation(request: AutomationActivateRequest):
    """
    Activate an automation from recommendation
    """
    try:
        # Get website
        website = await websites_collection.find_one({"_id": request.website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Get template
        template = await automation_templates_collection.find_one({"key": request.recommendation_key})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create active automation
        automation_id = str(uuid.uuid4())
        automation = {
            "_id": automation_id,
            "owner_id": "anonymous",
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
            "owner_id": "anonymous",
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


@app.get("/api/automations/{automation_id}")
async def get_automation(automation_id: str):
    """
    Get automation details
    """
    automation = await active_automations_collection.find_one({"_id": automation_id})
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return serialize_doc(automation)


@app.patch("/api/automations/{automation_id}")
async def update_automation(automation_id: str, updates: Dict[str, Any]):
    """
    Update automation config or status
    """
    updates["updated_at"] = datetime.now(timezone.utc)
    result = await active_automations_collection.update_one(
        {"_id": automation_id},
        {"$set": updates}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    automation = await active_automations_collection.find_one({"_id": automation_id})
    return serialize_doc(automation)


@app.get("/api/executions")
async def get_executions(workflow_id: str = None, limit: int = 50):
    """
    Get execution history
    """
    query = {"workflow_id": workflow_id} if workflow_id else {}
    executions = await executions_collection.find(query).sort("started_at", -1).limit(limit).to_list(length=limit)
    return serialize_docs(executions)


@app.post("/api/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: str, input_data: Dict[str, Any] = None):
    """
    Manually trigger a workflow execution
    """
    workflow = await workflows_collection.find_one({"_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    execution_id = await orchestrator.create_execution(workflow_id, "manual")
    await orchestrator.update_execution_state(execution_id, "running")
    await orchestrator.add_log(execution_id, "Workflow execution started")
    
    # Simulate execution (in production, this would be async worker)
    try:
        await orchestrator.add_log(execution_id, "Processing nodes...")
        # Add node execution logic here
        await orchestrator.update_execution_state(execution_id, "completed")
        await orchestrator.add_log(execution_id, "Workflow completed successfully")
    except Exception as e:
        await orchestrator.update_execution_state(execution_id, "failed", str(e))
        await orchestrator.add_log(execution_id, f"Workflow failed: {str(e)}")
    
    execution = await orchestrator.get_execution(execution_id)
    return serialize_doc(execution)


@app.get("/api/orchestrator/status")
async def get_orchestrator_status():
    """
    Get orchestrator queue and health status
    """
    return await orchestrator.get_queue_stats()


@app.get("/api/templates")
async def get_templates():
    """
    Get all automation templates
    """
    templates = await automation_templates_collection.find().to_list(length=100)
    return serialize_docs(templates)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
