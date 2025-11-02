"""
Usage tracking and plan limits enforcement
"""
from datetime import datetime, timezone
from typing import Dict

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

async def track_usage(db, user_id: str, ai_interactions: int = 0, chatbot_messages: int = 0):
    """
    Track usage for current month
    """
    month_key = datetime.now(timezone.utc).strftime("%Y-%m")
    usage_collection = db["usage"]
    
    # Upsert usage record
    await usage_collection.update_one(
        {"user_id": user_id, "month": month_key},
        {
            "$inc": {
                "ai_interactions": ai_interactions,
                "chatbot_messages": chatbot_messages
            },
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
        },
        upsert=True
    )

async def get_usage(db, user_id: str) -> Dict:
    """
    Get current month usage
    """
    month_key = datetime.now(timezone.utc).strftime("%Y-%m")
    usage_collection = db["usage"]
    
    usage = await usage_collection.find_one({"user_id": user_id, "month": month_key})
    
    if not usage:
        return {
            "ai_interactions": 0,
            "chatbot_messages": 0
        }
    
    return {
        "ai_interactions": usage.get("ai_interactions", 0),
        "chatbot_messages": usage.get("chatbot_messages", 0)
    }

async def check_limit(db, user_id: str, limit_type: str, plan: str) -> bool:
    """
    Check if user has reached their plan limit
    Returns True if within limits, False if exceeded
    """
    if limit_type == "ai_interactions":
        usage = await get_usage(db, user_id)
        current = usage.get("ai_interactions", 0)
        limit = PLAN_LIMITS[plan]["ai_interactions"]
        return current < limit
    
    elif limit_type == "websites":
        websites_collection = db["websites"]
        count = await websites_collection.count_documents({"owner_id": user_id})
        return count < PLAN_LIMITS[plan]["websites"]
    
    elif limit_type == "automations":
        automations_collection = db["active_automations"]
        count = await automations_collection.count_documents({"owner_id": user_id})
        return count < PLAN_LIMITS[plan]["automations"]
    
    return True
