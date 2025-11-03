"""
AI Email Assistant Service
Drafts email responses, creates campaigns, suggests improvements
"""
import os
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

async def draft_email_response(db, context: dict, user_id: str = None) -> dict:
    """
    Generate AI-powered email response
    
    Args:
        context: {original_email, tone, key_points, recipient_name}
    """
    prompt = f"""Draft a professional email response to the following:

Original Email:
{context.get('original_email', 'N/A')}

Response Guidelines:
- Recipient: {context.get('recipient_name', 'the sender')}
- Tone: {context.get('tone', 'professional and friendly')}
- Key Points to Address: {context.get('key_points', 'Acknowledge their message and provide helpful information')}

Write a clear, well-structured response that:
1. Acknowledges their message
2. Addresses all key points
3. Maintains appropriate tone
4. Includes clear next steps if needed
5. Has a professional closing

Do not include subject line."""
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"email-draft-{uuid.uuid4()}"
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Save draft
        draft_id = str(uuid.uuid4())
        await db["email_drafts"].insert_one({
            "_id": draft_id,
            "user_id": user_id or "system",
            "type": "response",
            "context": context,
            "draft": response,
            "created_at": datetime.now(timezone.utc)
        })
        
        return {
            "draft_id": draft_id,
            "draft": response
        }
        
    except Exception as e:
        print(f"Email draft error: {e}")
        raise Exception(f"Failed to generate email draft: {str(e)}")


async def create_email_campaign(db, campaign_data: dict, user_id: str = None) -> dict:
    """
    Generate email campaign with multiple variations
    
    Args:
        campaign_data: {topic, goal, audience, tone, num_variations}
    """
    prompt = f"""Create a marketing email campaign about {campaign_data.get('topic')}.

Campaign Details:
- Goal: {campaign_data.get('goal', 'Generate interest and drive action')}
- Target Audience: {campaign_data.get('audience', 'General business audience')}
- Tone: {campaign_data.get('tone', 'professional yet engaging')}

Generate {campaign_data.get('num_variations', 2)} email variations, each with:

1. Subject Line (create 2 options per email for A/B testing)
2. Preheader text
3. Email body (scannable, mobile-friendly)
4. Call-to-action (clear and compelling)

Format each email clearly with headers: Subject, Preheader, Body, CTA

Make them conversion-optimized and engaging."""
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"email-campaign-{uuid.uuid4()}"
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Save campaign
        campaign_id = str(uuid.uuid4())
        await db["email_campaigns"].insert_one({
            "_id": campaign_id,
            "user_id": user_id or "system",
            "campaign_data": campaign_data,
            "variations": response,
            "status": "draft",
            "created_at": datetime.now(timezone.utc)
        })
        
        return {
            "campaign_id": campaign_id,
            "variations": response
        }
        
    except Exception as e:
        print(f"Campaign generation error: {e}")
        raise Exception(f"Failed to generate campaign: {str(e)}")


async def get_email_drafts(db, user_id: str, limit: int = 50):
    """
    Get user's email draft history
    """
    items = await db["email_drafts"].find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return items
