"""
UTM tracking and lead attribution service
"""
from datetime import datetime, timezone
from typing import Optional, Dict

async def track_utm_source(db, lead_id: str, utm_params: Dict):
    """
    Track UTM parameters for lead attribution
    
    Args:
        utm_params: {utm_source, utm_medium, utm_campaign, utm_term, utm_content}
    """
    await db["utm_tracking"].insert_one({
        "lead_id": lead_id,
        "utm_source": utm_params.get('utm_source'),
        "utm_medium": utm_params.get('utm_medium'),
        "utm_campaign": utm_params.get('utm_campaign'),
        "utm_term": utm_params.get('utm_term'),
        "utm_content": utm_params.get('utm_content'),
        "tracked_at": datetime.now(timezone.utc)
    })

async def get_attribution_report(db, days: int = 30):
    """
    Get lead attribution report by UTM source
    """
    from datetime import timedelta
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Aggregate by source
    pipeline = [
        {"$match": {"tracked_at": {"$gte": start_date}}},
        {"$group": {
            "_id": "$utm_source",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    results = await db["utm_tracking"].aggregate(pipeline).to_list(100)
    
    return [
        {"source": r["_id"] or "direct", "leads": r["count"]}
        for r in results
    ]
