"""
Additional endpoints for Iteration 2 & 3: Lead Capture and Analytics
Append these to server.py
"""
from pydantic import BaseModel
from typing import Optional, List
from services.lead_service import generate_lead_autoresponse, score_lead
from services.analytics_service import get_dashboard_analytics, get_automation_performance

# ========== LEAD CAPTURE (PUBLIC) ==========
class FormSubmitRequest(BaseModel):
    form_id: str
    data: dict  # {name, email, phone, message, ...custom fields}

class FormCreateRequest(BaseModel):
    name: str
    website_id: str
    fields: List[dict]  # [{name, type, required}]
    settings: Optional[dict] = None

@app.post("/api/forms")
async def create_form(req: FormCreateRequest, user: dict = Depends(get_current_user)):
    """Create a lead capture form"""
    form_id = str(uuid.uuid4())
    form = {
        "_id": form_id,
        "owner_id": user["user_id"],
        "website_id": req.website_id,
        "name": req.name,
        "fields": req.fields,
        "settings": req.settings or {
            "autoresponse_enabled": True,
            "notification_email": user.get("email")
        },
        "created_at": datetime.now(timezone.utc)
    }
    await db["forms"].insert_one(form)
    return serialize_doc(form)


@app.get("/api/forms")
async def list_forms(user: dict = Depends(get_current_user)):
    """List user's forms"""
    items = await db["forms"].find({"owner_id": user["user_id"]}).to_list(100)
    return serialize_docs(items)


@app.get("/api/forms/{form_id}")
async def get_form(form_id: str, user: dict = Depends(get_current_user)):
    """Get form details"""
    form = await db["forms"].find_one({"_id": form_id, "owner_id": user["user_id"]})
    if not form:
        raise HTTPException(404, "Form not found")
    return serialize_doc(form)


@app.post("/api/forms/{form_id}/submit")
async def submit_form(form_id: str, req: FormSubmitRequest):
    """PUBLIC endpoint for form submissions"""
    forms = db["forms"]
    leads_col = db["leads"]
    
    # Get form
    form = await forms.find_one({"_id": form_id})
    if not form:
        raise HTTPException(404, "Form not found")
    
    # Validate required fields
    for field in form.get("fields", []):
        if field.get("required") and not req.data.get(field["name"]):
            raise HTTPException(400, f"Field '{field['name']}' is required")
    
    # Score lead
    score = await score_lead(db, req.data)
    
    # Store lead
    lead_id = str(uuid.uuid4())
    lead = {
        "_id": lead_id,
        "form_id": form_id,
        "website_id": form["website_id"],
        "owner_id": form["owner_id"],
        "data": req.data,
        "score": score,
        "status": "new",
        "autoresponse_sent": False,
        "created_at": datetime.now(timezone.utc)
    }
    await leads_col.insert_one(lead)
    
    # Track usage
    await track_usage(db, form["owner_id"], chatbot_messages=0, ai_interactions=1)
    
    # Generate AI auto-response
    autoresponse = None
    if form.get("settings", {}).get("autoresponse_enabled", True):
        autoresponse = await generate_lead_autoresponse(db, req.data, form["website_id"])
        await leads_col.update_one(
            {"_id": lead_id},
            {"$set": {"autoresponse_sent": True, "autoresponse_content": autoresponse}}
        )
    
    return {
        "success": True,
        "lead_id": lead_id,
        "autoresponse": autoresponse,
        "message": "Thank you! We'll be in touch soon."
    }


@app.get("/api/leads")
async def list_leads(user: dict = Depends(get_current_user), form_id: str = None):
    """List leads"""
    query = {"owner_id": user["user_id"]}
    if form_id:
        query["form_id"] = form_id
    
    items = await db["leads"].find(query).sort("created_at", -1).limit(100).to_list(100)
    return serialize_docs(items)


@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str, user: dict = Depends(get_current_user)):
    """Get lead details"""
    lead = await db["leads"].find_one({"_id": lead_id, "owner_id": user["user_id"]})
    if not lead:
        raise HTTPException(404, "Lead not found")
    return serialize_doc(lead)


@app.patch("/api/leads/{lead_id}")
async def update_lead(lead_id: str, updates: dict, user: dict = Depends(get_current_user)):
    """Update lead status"""
    result = await db["leads"].update_one(
        {"_id": lead_id, "owner_id": user["user_id"]},
        {"$set": {**updates, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Lead not found")
    
    lead = await db["leads"].find_one({"_id": lead_id})
    return serialize_doc(lead)


# ========== ANALYTICS ==========
@app.get("/api/analytics/dashboard")
async def get_analytics(user: dict = Depends(get_current_user), days: int = 30):
    """Get dashboard analytics"""
    analytics = await get_dashboard_analytics(db, user["user_id"], days)
    return analytics


@app.get("/api/analytics/automation/{automation_id}")
async def get_automation_analytics(automation_id: str, user: dict = Depends(get_current_user), days: int = 30):
    """Get automation performance"""
    # Verify ownership
    automation = await db["active_automations"].find_one({"_id": automation_id, "owner_id": user["user_id"]})
    if not automation:
        raise HTTPException(404, "Automation not found")
    
    performance = await get_automation_performance(db, automation_id, days)
    return performance


# ========== ENHANCED ORCHESTRATOR ==========
@app.get("/api/orchestrator/logs/{execution_id}")
async def get_execution_logs(execution_id: str, user: dict = Depends(get_current_user)):
    """Get execution logs"""
    execution = await db["executions"].find_one({"_id": execution_id})
    if not execution:
        raise HTTPException(404, "Execution not found")
    
    return {
        "execution_id": execution_id,
        "logs": execution.get("logs", []),
        "state": execution.get("state"),
        "error": execution.get("error")
    }


@app.post("/api/orchestrator/retry/{execution_id}")
async def retry_execution(execution_id: str, user: dict = Depends(get_current_user)):
    """Retry a failed execution"""
    execution = await db["executions"].find_one({"_id": execution_id})
    if not execution:
        raise HTTPException(404, "Execution not found")
    
    if execution.get("state") != "failed":
        raise HTTPException(400, "Can only retry failed executions")
    
    # Create new execution
    workflow_id = execution["workflow_id"]
    new_exec_id = await orchestrator.create_execution(workflow_id, "manual_retry")
    await orchestrator.add_log(new_exec_id, f"Retrying failed execution {execution_id}")
    await orchestrator.update_execution_state(new_exec_id, "completed")
    
    return {"new_execution_id": new_exec_id, "message": "Execution retried"}
