"""
AI Chatbot service for processing chat messages
"""
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime, timezone
import uuid

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

async def process_chatbot_message(db, website_id: str, session_id: str, message: str, user_message_only: bool = False) -> dict:
    """
    Process chatbot message and return AI response
    """
    messages_collection = db["chatbot_messages"]
    sessions_collection = db["chatbot_sessions"]
    websites_collection = db["websites"]
    
    # Get website context
    website = await websites_collection.find_one({"_id": website_id})
    if not website:
        return {"error": "Website not found"}
    
    website_context = f"""
You are a helpful customer support agent for {website.get('title', 'this website')}.
Website: {website.get('url')}
Business Type: {website.get('business_type')}
Context: {website.get('content_digest', '')}

Be helpful, professional, and provide accurate information based on the website content.
"""
    
    # Get or create session
    session = await sessions_collection.find_one({"_id": session_id})
    if not session:
        session = {
            "_id": session_id,
            "website_id": website_id,
            "started_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "messages_count": 0,
            "status": "active"
        }
        await sessions_collection.insert_one(session)
    
    # Store user message
    user_msg_id = str(uuid.uuid4())
    user_msg = {
        "_id": user_msg_id,
        "website_id": website_id,
        "session_id": session_id,
        "role": "user",
        "content": message,
        "timestamp": datetime.now(timezone.utc)
    }
    await messages_collection.insert_one(user_msg)
    
    if user_message_only:
        return {"message_id": user_msg_id}
    
    # Get conversation history (last 10 messages)
    history = await messages_collection.find(
        {"session_id": session_id}
    ).sort("timestamp", -1).limit(10).to_list(length=10)
    history.reverse()  # Oldest first
    
    # Generate AI response
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"chatbot-{session_id}",
            system_message=website_context
        ).with_model("openai", "gpt-4o-mini")  # Using mini for cost efficiency
        
        user_message_obj = UserMessage(text=message)
        response = await chat.send_message(user_message_obj)
        
        # Store AI response
        ai_msg_id = str(uuid.uuid4())
        ai_msg = {
            "_id": ai_msg_id,
            "website_id": website_id,
            "session_id": session_id,
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now(timezone.utc)
        }
        await messages_collection.insert_one(ai_msg)
        
        # Update session
        await sessions_collection.update_one(
            {"_id": session_id},
            {
                "$set": {"last_activity": datetime.now(timezone.utc)},
                "$inc": {"messages_count": 2}
            }
        )
        
        return {
            "response": response,
            "message_id": ai_msg_id,
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"Chatbot error: {e}")
        # Return fallback response
        fallback = "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment."
        ai_msg_id = str(uuid.uuid4())
        ai_msg = {
            "_id": ai_msg_id,
            "website_id": website_id,
            "session_id": session_id,
            "role": "assistant",
            "content": fallback,
            "timestamp": datetime.now(timezone.utc)
        }
        await messages_collection.insert_one(ai_msg)
        
        return {
            "response": fallback,
            "message_id": ai_msg_id,
            "session_id": session_id,
            "error": str(e)
        }


async def get_chatbot_history(db, session_id: str, limit: int = 50):
    """
    Get chat history for a session
    """
    messages_collection = db["chatbot_messages"]
    
    messages = await messages_collection.find(
        {"session_id": session_id}
    ).sort("timestamp", 1).limit(limit).to_list(length=limit)
    
    return messages
