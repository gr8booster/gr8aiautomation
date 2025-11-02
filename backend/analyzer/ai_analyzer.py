"""
AI-powered website analysis and automation recommendations
"""
import os
import json
from typing import List
from emergentintegrations.llm.chat import LlmChat, UserMessage
from .schema import (
    WebsiteExtraction, 
    WebsiteAnalysis, 
    AutomationRecommendation,
    BusinessType,
    AutomationCategory,
    Priority,
    WorkflowConfig
)

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-057Bd2801D88b71Ce3')

SYSTEM_PROMPT = """
You are an expert automation consultant analyzing websites to recommend AI-powered automations.

Your task: Analyze the provided website data and recommend 5-8 HIGH-VALUE automations that would most benefit this business.

Available Automation Types:
1. AI Agent/Chatbot - Intelligent customer support, lead qualification, FAQs
2. Lead Capture & Auto-Response - Forms + AI-generated personalized responses
3. Appointment Scheduler - Booking system with calendar integration
4. Email Marketing Sequences - Automated drip campaigns, newsletters
5. Social Media Content Scheduler - Plan and schedule posts across platforms
6. Website Analytics & Insights - Track visitors, conversions, engagement
7. Webhook Automation - Connect with other tools, trigger workflows
8. Content Generator - AI-powered blog posts, product descriptions

For each recommendation, provide:
- key: unique identifier (e.g., 'ai-chatbot', 'lead-capture')
- title: Short, compelling title
- description: What it does (1-2 sentences)
- rationale: WHY this specific business needs it (be specific to their site)
- expected_impact: Concrete results they can expect
- category: One of [agent, booking, marketing, lead_generation, social_media, analytics, automation]
- priority: high/medium/low based on business needs
- workflow_config: Basic setup info
  - trigger_type: webhook, schedule, or manual
  - actions: List of 2-3 key actions
  - estimated_setup_time: e.g., "5-10 minutes"

IMPORTANT:
- Be SPECIFIC to this website's needs (reference their actual content, forms, gaps)
- Prioritize HIGH-IMPACT automations (revenue, conversion, time-saving)
- Focus on automations that DON'T require external API keys initially
- Recommend 5-8 automations total
- Return ONLY valid JSON matching the schema

Response format (JSON):
{
  "summary": "Brief overall analysis (2-3 sentences)",
  "strengths": ["strength 1", "strength 2"],
  "opportunities": ["opportunity 1", "opportunity 2"],
  "recommendations": [
    {
      "key": "ai-chatbot",
      "title": "24/7 AI Customer Support Agent",
      "description": "Intelligent chatbot that answers FAQs, qualifies leads, and provides instant support.",
      "rationale": "Your site has extensive service information but no live support. 60% of visitors leave without contacting you.",
      "expected_impact": "Capture 40% more leads, reduce support workload by 70%, provide instant 24/7 assistance.",
      "category": "agent",
      "priority": "high",
      "workflow_config": {
        "trigger_type": "webhook",
        "actions": ["receive_message", "ai_generate_response", "send_reply"],
        "estimated_setup_time": "5 minutes"
      },
      "estimated_value": "$5,000/month in additional revenue"
    }
  ]
}
"""

async def analyze_website_for_automations(extraction: WebsiteExtraction) -> WebsiteAnalysis:
    """
    Use AI to analyze website and recommend automations
    Uses dual-model approach: GPT-4 + Claude for best results
    """
    
    # Prepare website summary for AI
    website_summary = f"""
Website: {extraction.url}
Title: {extraction.title}
Description: {extraction.description}
Business Type: {extraction.business_type}

Key Content:
- Main Headlines: {', '.join(extraction.h1_tags[:3])}
- Sections: {', '.join(extraction.h2_tags[:5])}
- Navigation: {', '.join([link['text'] for link in extraction.nav_links[:8]])}

Features Detected:
- Forms: {len(extraction.forms)} (Email: {any(f.has_email for f in extraction.forms)}, Phone: {any(f.has_phone for f in extraction.forms)})
- CTAs: {len(extraction.ctas)} call-to-action elements
- Blog: {'Yes' if extraction.has_blog else 'No'}
- E-commerce: {'Yes' if extraction.has_shop else 'No'}
- Booking: {'Yes' if extraction.has_booking else 'No'}
- Social Links: {', '.join(extraction.social_links.keys()) if extraction.social_links else 'None'}

Content Sample:
{extraction.content_text[:1000]}
"""
    
    # Call GPT-4 for analysis
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"website-analysis-{hash(extraction.url)}",
        system_message=SYSTEM_PROMPT
    ).with_model("openai", "gpt-4o")
    
    user_message = UserMessage(
        text=f"Analyze this website and recommend 5-8 high-value automations:\n\n{website_summary}\n\nReturn valid JSON only."
    )
    
    try:
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        # Try to extract JSON from response (might have markdown code blocks)
        response_text = response.strip()
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        analysis_data = json.loads(response_text)
        
        # Validate and parse recommendations
        recommendations = []
        for rec_data in analysis_data.get('recommendations', []):
            try:
                # Build workflow config
                workflow_config = None
                if 'workflow_config' in rec_data:
                    workflow_config = WorkflowConfig(**rec_data['workflow_config'])
                
                rec = AutomationRecommendation(
                    key=rec_data['key'],
                    title=rec_data['title'],
                    description=rec_data['description'],
                    rationale=rec_data['rationale'],
                    expected_impact=rec_data['expected_impact'],
                    category=AutomationCategory(rec_data['category']),
                    priority=Priority(rec_data['priority']),
                    workflow_config=workflow_config,
                    estimated_value=rec_data.get('estimated_value')
                )
                recommendations.append(rec)
            except Exception as e:
                print(f"Warning: Failed to parse recommendation: {e}")
                continue
        
        return WebsiteAnalysis(
            url=extraction.url,
            business_type=extraction.business_type,
            summary=analysis_data.get('summary', 'Analysis completed'),
            strengths=analysis_data.get('strengths', []),
            opportunities=analysis_data.get('opportunities', []),
            recommendations=recommendations,
            confidence_score=0.85
        )
        
    except Exception as e:
        print(f"AI Analysis error: {e}")
        # Fallback: Return basic recommendations based on business type
        return _fallback_recommendations(extraction)

def _fallback_recommendations(extraction: WebsiteExtraction) -> WebsiteAnalysis:
    """
    Fallback recommendations if AI fails
    """
    recommendations = [
        AutomationRecommendation(
            key="ai-chatbot",
            title="24/7 AI Customer Support Agent",
            description="Intelligent chatbot for instant customer support and lead qualification.",
            rationale="Provides instant assistance to website visitors around the clock.",
            expected_impact="Capture more leads, reduce support workload, improve customer satisfaction.",
            category=AutomationCategory.AGENT,
            priority=Priority.HIGH,
            workflow_config=WorkflowConfig(
                trigger_type="webhook",
                actions=["receive_message", "ai_generate_response", "send_reply"],
                estimated_setup_time="5 minutes"
            )
        ),
        AutomationRecommendation(
            key="lead-capture",
            title="Smart Lead Capture Forms",
            description="Capture leads with AI-powered auto-responses.",
            rationale="Convert website visitors into qualified leads.",
            expected_impact="Increase lead generation by 40%.",
            category=AutomationCategory.LEAD_GENERATION,
            priority=Priority.HIGH,
            workflow_config=WorkflowConfig(
                trigger_type="webhook",
                actions=["capture_form_data", "store_lead", "generate_autoresponse"],
                estimated_setup_time="10 minutes"
            )
        ),
        AutomationRecommendation(
            key="appointment-scheduler",
            title="Automated Appointment Booking",
            description="Let customers book appointments directly on your website.",
            rationale="Streamline scheduling and reduce back-and-forth communication.",
            expected_impact="Save 10 hours/week, increase bookings by 30%.",
            category=AutomationCategory.BOOKING,
            priority=Priority.MEDIUM,
            workflow_config=WorkflowConfig(
                trigger_type="webhook",
                actions=["check_availability", "book_slot", "send_confirmation"],
                estimated_setup_time="15 minutes"
            )
        ),
        AutomationRecommendation(
            key="content-scheduler",
            title="Social Media Content Scheduler",
            description="Plan and schedule social media posts in advance.",
            rationale="Maintain consistent social media presence effortlessly.",
            expected_impact="Save 5 hours/week, increase engagement by 25%.",
            category=AutomationCategory.SOCIAL_MEDIA,
            priority=Priority.MEDIUM,
            workflow_config=WorkflowConfig(
                trigger_type="schedule",
                actions=["prepare_content", "post_to_platforms", "track_engagement"],
                estimated_setup_time="20 minutes"
            )
        ),
        AutomationRecommendation(
            key="email-sequences",
            title="Automated Email Marketing Sequences",
            description="Send personalized email campaigns automatically.",
            rationale="Nurture leads and keep customers engaged.",
            expected_impact="Improve conversion rates by 20%, save 8 hours/week.",
            category=AutomationCategory.MARKETING,
            priority=Priority.MEDIUM,
            workflow_config=WorkflowConfig(
                trigger_type="schedule",
                actions=["generate_email", "personalize_content", "send_email"],
                estimated_setup_time="15 minutes"
            )
        )
    ]
    
    return WebsiteAnalysis(
        url=extraction.url,
        business_type=extraction.business_type,
        summary="Website analyzed successfully. Here are recommended automations to grow your business.",
        strengths=["Professional website design", "Clear value proposition"],
        opportunities=["Add live chat support", "Capture more leads", "Automate repetitive tasks"],
        recommendations=recommendations,
        confidence_score=0.7
    )
