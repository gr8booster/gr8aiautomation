"""
AI Content Generator Service
Generates blog posts, product descriptions, marketing copy, social media posts
"""
import os
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

CONTENT_TEMPLATES = {
    "blog_post": {
        "name": "Blog Post",
        "prompt": """Write a comprehensive, engaging blog post about {topic}.
        
Tone: {tone}
Length: {length} words
Target Audience: {audience}
        
Include:
- Compelling headline
- Introduction hook
- 3-5 main sections with subheadings
- Practical examples or tips
- Conclusion with call-to-action
- SEO-friendly structure
        
Make it informative, well-structured, and valuable to readers."""
    },
    "product_description": {
        "name": "Product Description",
        "prompt": """Write a compelling product description for {product_name}.
        
Product Details: {product_details}
Target Audience: {audience}
Tone: {tone}
        
Include:
- Attention-grabbing headline
- Key features and benefits (focus on benefits)
- Unique selling points
- Social proof or credibility elements
- Clear call-to-action
        
Make it persuasive and conversion-focused. Length: {length} words."""
    },
    "social_media": {
        "name": "Social Media Post",
        "prompt": """Create {count} engaging social media posts about {topic}.
        
Platform: {platform}
Tone: {tone}
Goal: {goal}
        
For each post:
- Hook in first line
- Value-driven content
- Include relevant hashtags (3-5)
- Call-to-action
- Platform-appropriate length
        
Make them scroll-stopping and shareable."""
    },
    "email_campaign": {
        "name": "Email Campaign",
        "prompt": """Write a marketing email for {topic}.
        
Campaign Goal: {goal}
Target Audience: {audience}
Tone: {tone}
        
Include:
- Compelling subject line (A/B test options)
- Personalized greeting
- Clear value proposition
- Scannable content (bullets/short paragraphs)
- Strong call-to-action
- P.S. line for additional engagement
        
Make it conversion-focused and mobile-friendly."""
    },
    "ad_copy": {
        "name": "Ad Copy",
        "prompt": """Create {count} ad variations for {product_name}.
        
Platform: {platform}
Goal: {goal}
Target Audience: {audience}
        
For each ad:
- Attention-grabbing headline
- Benefit-focused body copy
- Strong call-to-action
- Platform character limits respected
        
Make them click-worthy and conversion-optimized."""
    }
}

async def generate_content(db, content_type: str, inputs: dict, user_id: str = None) -> dict:
    """
    Generate AI content based on type and inputs
    """
    if content_type not in CONTENT_TEMPLATES:
        raise ValueError(f"Unknown content type: {content_type}")
    
    template = CONTENT_TEMPLATES[content_type]
    
    # Format prompt with inputs
    try:
        prompt = template["prompt"].format(**inputs)
    except KeyError as e:
        raise ValueError(f"Missing required input: {e}")
    
    # Generate with AI
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"content-{uuid.uuid4()}"
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Save to database
        content_id = str(uuid.uuid4())
        await db["generated_content"].insert_one({
            "_id": content_id,
            "user_id": user_id or "system",
            "content_type": content_type,
            "inputs": inputs,
            "output": response,
            "created_at": datetime.now(timezone.utc)
        })
        
        return {
            "content_id": content_id,
            "content_type": content_type,
            "output": response,
            "word_count": len(response.split())
        }
        
    except Exception as e:
        print(f"Content generation error: {e}")
        raise Exception(f"AI content generation failed: {str(e)}")


async def get_content_history(db, user_id: str, limit: int = 50):
    """
    Get user's content generation history
    """
    items = await db["generated_content"].find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return items
