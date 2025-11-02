"""
Analytics service for generating insights and metrics
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List

async def get_dashboard_analytics(db, user_id: str, days: int = 30) -> Dict:
    """
    Get comprehensive analytics for dashboard
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Collections
    automations = db["active_automations"]
    executions = db["executions"]
    chatbot_messages = db["chatbot_messages"]
    leads = db["leads"]
    websites = db["websites"]
    
    # Get user's website IDs
    website_docs = await websites.find({"owner_id": user_id}).to_list(100)
    website_ids = [w["_id"] for w in website_docs]
    
    # Automation stats
    total_automations = await automations.count_documents({"owner_id": user_id})
    active_automations = await automations.count_documents({"owner_id": user_id, "status": "active"})
    
    # Execution stats
    total_executions = await executions.count_documents({"started_at": {"$gte": start_date}})
    successful_executions = await executions.count_documents({
        "state": "completed",
        "started_at": {"$gte": start_date}
    })
    failed_executions = await executions.count_documents({
        "state": "failed",
        "started_at": {"$gte": start_date}
    })
    
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
    
    # Chatbot stats
    total_messages = await chatbot_messages.count_documents({
        "website_id": {"$in": website_ids},
        "timestamp": {"$gte": start_date}
    })
    
    unique_sessions = len(await chatbot_messages.distinct(
        "session_id",
        {"website_id": {"$in": website_ids}, "timestamp": {"$gte": start_date}}
    ))
    
    # Lead stats
    total_leads = await leads.count_documents({
        "website_id": {"$in": website_ids},
        "created_at": {"$gte": start_date}
    })
    
    hot_leads = await leads.count_documents({
        "website_id": {"$in": website_ids},
        "score": "hot",
        "created_at": {"$gte": start_date}
    })
    
    # Time series data (last 7 days)
    time_series = []
    for i in range(7):
        day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6-i)
        day_end = day_start + timedelta(days=1)
        
        day_executions = await executions.count_documents({
            "started_at": {"$gte": day_start, "$lt": day_end}
        })
        
        day_messages = await chatbot_messages.count_documents({
            "website_id": {"$in": website_ids},
            "timestamp": {"$gte": day_start, "$lt": day_end}
        })
        
        day_leads = await leads.count_documents({
            "website_id": {"$in": website_ids},
            "created_at": {"$gte": day_start, "$lt": day_end}
        })
        
        time_series.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "executions": day_executions,
            "messages": day_messages,
            "leads": day_leads
        })
    
    return {
        "overview": {
            "total_automations": total_automations,
            "active_automations": active_automations,
            "total_executions": total_executions,
            "success_rate": round(success_rate, 1),
            "failed_executions": failed_executions
        },
        "chatbot": {
            "total_messages": total_messages,
            "unique_sessions": unique_sessions,
            "avg_messages_per_session": round(total_messages / unique_sessions, 1) if unique_sessions > 0 else 0
        },
        "leads": {
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "conversion_rate": round(hot_leads / total_leads * 100, 1) if total_leads > 0 else 0
        },
        "time_series": time_series,
        "period_days": days
    }


async def get_automation_performance(db, automation_id: str, days: int = 30) -> Dict:
    """
    Get performance metrics for specific automation
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    workflows = db["workflows"]
    executions = db["executions"]
    
    # Get workflow for this automation
    workflow = await workflows.find_one({"automation_id": automation_id})
    if not workflow:
        return {"error": "Workflow not found"}
    
    # Execution stats
    total_runs = await executions.count_documents({
        "workflow_id": workflow["_id"],
        "started_at": {"$gte": start_date}
    })
    
    successful_runs = await executions.count_documents({
        "workflow_id": workflow["_id"],
        "state": "completed",
        "started_at": {"$gte": start_date}
    })
    
    failed_runs = await executions.count_documents({
        "workflow_id": workflow["_id"],
        "state": "failed",
        "started_at": {"$gte": start_date}
    })
    
    # Average execution time
    completed_executions = await executions.find({
        "workflow_id": workflow["_id"],
        "state": "completed",
        "finished_at": {"$exists": True}
    }).to_list(100)
    
    if completed_executions:
        durations = []
        for exec in completed_executions:
            if exec.get("finished_at") and exec.get("started_at"):
                duration = (exec["finished_at"] - exec["started_at"]).total_seconds()
                durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
    else:
        avg_duration = 0
    
    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "success_rate": round(successful_runs / total_runs * 100, 1) if total_runs > 0 else 0,
        "avg_duration_seconds": round(avg_duration, 2),
        "period_days": days
    }
