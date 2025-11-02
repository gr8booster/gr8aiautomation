"""
Lead Capture service for processing form submissions and AI auto-responses
"""
import os
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

async def generate_lead_autoresponse(db, lead_data: dict, website_id: str) -> str:
    """
    Generate AI-powered personalized auto-response for lead
    """
    websites_collection = db["websites"]
    
    # Get website context
    website = await websites_collection.find_one({"_id": website_id})
    if not website:
        return "Thank you for your interest! We'll get back to you soon."
    
    # Build context for AI
    context = f"""
You are responding to a lead/inquiry for {website.get('title', 'our company')}.

Website: {website.get('url')}
Business Type: {website.get('business_type')}

Lead Information:
Name: {lead_data.get('name', 'Not provided')}
Email: {lead_data.get('email')}
Message: {lead_data.get('message', 'No message provided')}

Write a warm, professional, personalized auto-response email that:
1. Thanks them for their interest
2. Acknowledges their specific question/message
3. Provides helpful next steps
4. Sets expectations for follow-up
5. Maintains a tone appropriate for the business type

Keep it concise (3-4 short paragraphs). Do not include subject line or email signature.
"""
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"lead-{uuid.uuid4()}",
            system_message="You are a helpful business assistant writing professional auto-response emails."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=context)
        response = await chat.send_message(user_message)
        
        return response
        
    except Exception as e:
        print(f"Auto-response generation error: {e}")
        # Fallback response
        return f"""Thank you for reaching out to us!

We've received your message and appreciate your interest. One of our team members will review your inquiry and get back to you within 24 hours.

In the meantime, feel free to explore our website at {website.get('url')} for more information.

Best regards,
The Team"""


async def score_lead(db, lead_data: dict) -> str:
    """
    Use AI to score lead as hot/warm/cold
    """
    try:
        prompt = f"""
Score this lead as HOT, WARM, or COLD based on the provided information.

Lead Data:
- Name: {lead_data.get('name', 'Not provided')}
- Email: {lead_data.get('email')}
- Phone: {lead_data.get('phone', 'Not provided')}
- Company: {lead_data.get('company', 'Not provided')}
- Message: {lead_data.get('message', 'No message')}

Criteria:
- HOT: Clear buying intent, specific requirements, contact info provided, urgent need
- WARM: Interested, some details provided, not urgent
- COLD: Generic inquiry, minimal info, unclear intent

Respond with ONLY one word: HOT, WARM, or COLD
"""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"lead-score-{uuid.uuid4()}"
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(UserMessage(text=prompt))
        score = response.strip().upper()
        
        if score in ['HOT', 'WARM', 'COLD']:
            return score.lower()
        return 'warm'  # Default
        
    except Exception as e:
        print(f"Lead scoring error: {e}")
        return 'warm'
