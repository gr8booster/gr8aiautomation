"""
AI Workforce Intelligence Scanner
Analyzes job postings and maps them to AI agent replacements
"""
import os
import re
from bs4 import BeautifulSoup
import httpx
from typing import List, Dict
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Average annual salaries by role (US market, 2024)
ROLE_SALARY_MAP = {
    "customer service": 38000,
    "sales": 55000,
    "marketing": 52000,
    "appointment setter": 35000,
    "data entry": 32000,
    "administrative": 42000,
    "support": 40000,
    "coordinator": 45000,
    "assistant": 38000,
    "representative": 42000
}

# AI Agent pricing (monthly)
AI_AGENT_COST = 99  # Pro plan per month = $1188/year

async def extract_job_postings(url: str) -> List[Dict]:
    """
    Scan website for job postings on careers/jobs pages
    """
    job_pages_found = []
    job_postings = []
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            # Try common job page URLs
            career_paths = [
                '/careers', '/jobs', '/join-us', '/team', '/about/careers',
                '/company/careers', '/work-with-us', '/opportunities'
            ]
            
            for path in career_paths:
                try:
                    job_url = url.rstrip('/') + path
                    response = await client.get(job_url)
                    
                    if response.status_code == 200:
                        job_pages_found.append(job_url)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract job titles and descriptions
                        # Look for common patterns
                        for heading in soup.find_all(['h2', 'h3', 'h4']):
                            text = heading.get_text().strip()
                            
                            # Check if it looks like a job title
                            if any(keyword in text.lower() for keyword in [
                                'customer', 'sales', 'marketing', 'support', 'service',
                                'manager', 'specialist', 'coordinator', 'representative',
                                'assistant', 'engineer', 'developer', 'analyst', 'designer'
                            ]):
                                # Get description from next siblings
                                description = ""
                                next_elem = heading.find_next_sibling()
                                if next_elem:
                                    description = next_elem.get_text().strip()[:500]
                                
                                job_postings.append({
                                    "title": text,
                                    "description": description,
                                    "source_url": job_url
                                })
                
                except:
                    continue
        
        # If no structured job pages, scan main page for job-related content
        if not job_postings:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for "hiring", "join our team" sections
                for section in soup.find_all(['div', 'section'], class_=re.compile(r'career|job|hiring|team', re.I)):
                    headings = section.find_all(['h2', 'h3', 'h4'])
                    for h in headings[:5]:  # Limit to 5
                        job_postings.append({
                            "title": h.get_text().strip(),
                            "description": "",
                            "source_url": url
                        })
            except:
                pass
    
    except Exception as e:
        print(f"Job extraction error: {e}")
    
    return job_postings[:10]  # Limit to 10 jobs


async def map_job_to_ai_agent(job_title: str, job_description: str) -> Dict:
    """
    Use AI to map a job role to GR8 AI agent recommendation
    """
    prompt = f"""Analyze this job role and recommend which GR8 AI Agent(s) could replace or assist:

Job Title: {job_title}
Description: {job_description}

Available GR8 AI Agents:
1. AI Chat Support Agent - Handles customer inquiries 24/7
2. AI Sales Assistant - Qualifies leads, handles basic sales questions
3. AI Appointment Scheduler - Books meetings automatically
4. AI Email Assistant - Drafts responses, manages inbox
5. AI Content Generator - Creates marketing copy, blog posts
6. AI Lead Capture Agent - Captures and qualifies leads
7. AI Workflow Automator - Handles repetitive tasks

For this role, provide:
1. Primary AI Agent recommendation (choose 1-2 from above)
2. Automation potential (0-100%)
3. Role classification: Full Replacement, Assistant, or Hybrid
4. Key tasks that can be automated
5. Brief explanation

Respond in JSON:
{{
  "ai_agent": "Primary agent name",
  "secondary_agent": "Secondary agent or null",
  "automation_potential": 85,
  "classification": "Full Replacement|Assistant|Hybrid",
  "automated_tasks": ["task 1", "task 2", "task 3"],
  "explanation": "Brief explanation of how AI can help"
}}"""
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            system_message="You are a workforce automation expert analyzing job roles."
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse JSON
        import json
        response_text = response.strip()
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        mapping = json.loads(response_text)
        
        # Calculate cost savings
        estimated_salary = estimate_role_salary(job_title)
        annual_ai_cost = AI_AGENT_COST * 12
        annual_savings = estimated_salary - annual_ai_cost
        monthly_savings = annual_savings / 12
        
        mapping['estimated_annual_salary'] = estimated_salary
        mapping['ai_annual_cost'] = annual_ai_cost
        mapping['annual_savings'] = annual_savings
        mapping['monthly_savings'] = int(monthly_savings)
        
        return mapping
        
    except Exception as e:
        print(f"Job mapping error: {e}")
        return {
            "ai_agent": "AI Workflow Automator",
            "secondary_agent": None,
            "automation_potential": 50,
            "classification": "Assistant",
            "automated_tasks": ["Automate repetitive tasks"],
            "explanation": "General automation can improve efficiency",
            "estimated_annual_salary": 45000,
            "ai_annual_cost": AI_AGENT_COST * 12,
            "annual_savings": 45000 - (AI_AGENT_COST * 12),
            "monthly_savings": int((45000 - (AI_AGENT_COST * 12)) / 12)
        }


def estimate_role_salary(job_title: str) -> int:
    """
    Estimate annual salary based on job title keywords
    """
    title_lower = job_title.lower()
    
    for keyword, salary in ROLE_SALARY_MAP.items():
        if keyword in title_lower:
            return salary
    
    # Default if no match
    if 'manager' in title_lower or 'director' in title_lower:
        return 75000
    elif 'senior' in title_lower or 'lead' in title_lower:
        return 65000
    else:
        return 45000  # Default mid-level


async def analyze_workforce_opportunities(url: str) -> Dict:
    """
    Complete workforce analysis combining job scan and AI mapping
    """
    # Extract jobs
    jobs = await extract_job_postings(url)
    
    if not jobs:
        return {
            "jobs_found": 0,
            "workforce_opportunities": [],
            "total_potential_savings": 0,
            "summary": "No job postings found on this website."
        }
    
    # Map each job to AI agent
    opportunities = []
    total_savings = 0
    
    for job in jobs:
        mapping = await map_job_to_ai_agent(job['title'], job['description'])
        
        opportunities.append({
            "job_title": job['title'],
            "job_description": job['description'][:200],
            "ai_agent": mapping['ai_agent'],
            "secondary_agent": mapping.get('secondary_agent'),
            "automation_potential": mapping['automation_potential'],
            "classification": mapping['classification'],
            "automated_tasks": mapping['automated_tasks'],
            "explanation": mapping['explanation'],
            "monthly_savings": mapping['monthly_savings'],
            "annual_savings": mapping['annual_savings']
        })
        
        total_savings += mapping['monthly_savings']
    
    return {
        "jobs_found": len(jobs),
        "workforce_opportunities": opportunities,
        "total_potential_savings_monthly": int(total_savings),
        "total_potential_savings_annual": int(total_savings * 12),
        "summary": f"Found {len(jobs)} job roles with potential for AI augmentation or replacement. Estimated savings: ${int(total_savings):,}/month"
    }
