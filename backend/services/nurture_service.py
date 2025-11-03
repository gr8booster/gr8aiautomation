"""
Email nurture sequence for lead magnet system
Sends 3-email sequence after report generation
"""
import os
import asyncio
from datetime import datetime, timedelta, timezone
from services.email_service import send_email, EmailDeliveryError

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@gr8ai.com')
SENDER_NAME = os.environ.get('SENDER_NAME', 'GR8 AI Automation')

async def send_report_email(lead_email: str, lead_name: str, report_url: str, opportunities_count: int):
    """
    Email 1: Send the automation report
    """
    subject = f"🚀 Your AI Automation Report is Ready, {lead_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #374151;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #0c969b 0%, #0a7a7e 100%);
                color: white;
                padding: 30px 20px;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .content {{
                background: white;
                padding: 30px 20px;
                border-radius: 0 0 8px 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .highlight {{
                background: #f0fdfa;
                border-left: 4px solid #0c969b;
                padding: 15px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background: #0c969b;
                color: white;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
                font-weight: 600;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
            }}
            .stat-box {{
                text-align: center;
                padding: 15px;
                background: #f9fafb;
                border-radius: 8px;
            }}
            .stat-number {{
                font-size: 32px;
                font-weight: bold;
                color: #0c969b;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin: 0;">✨ Your Automation Report is Ready!</h1>
        </div>
        <div class="content">
            <p>Hi {lead_name},</p>
            
            <p>Great news! We've completed the AI-powered analysis of your website and discovered <strong>{opportunities_count} automation opportunities</strong> that could transform your business.</p>
            
            <div class="highlight">
                <h3 style="margin-top: 0;">📊 What's Inside Your Report:</h3>
                <ul>
                    <li><strong>Personalized automation roadmap</strong> for your business</li>
                    <li><strong>ROI estimates</strong> for each recommended automation</li>
                    <li><strong>Priority rankings</strong> to help you start with quick wins</li>
                    <li><strong>Implementation guides</strong> to deploy in minutes</li>
                </ul>
            </div>
            
            <div style="text-align: center;">
                <a href="{report_url}" class="button">📥 Download Your Full Report</a>
            </div>
            
            <p><strong>Here's a quick preview of what we found:</strong></p>
            <p>Your website has high potential for automation in customer support, lead capture, and scheduling. The full report breaks down exactly how each automation can save you time and increase revenue.</p>
            
            <div class="highlight">
                <p><strong>💡 Next Step:</strong> Review your report and pick 1-2 high-priority automations to implement first. We recommend starting with our AI Chatbot for immediate impact.</p>
            </div>
            
            <p>Want to activate these automations? <a href="https://gr8ai.com/login">Sign up for free</a> and deploy your first automation in under 5 minutes.</p>
            
            <p>Questions? Just reply to this email—I'm here to help!</p>
            
            <p>Best regards,<br>
            <strong>The GR8 AI Team</strong></p>
        </div>
    </body>
    </html>
    """
    
    try:
        await send_email(
            to_email=lead_email,
            subject=subject,
            html_content=html_content
        )
        return True
    except EmailDeliveryError as e:
        print(f"Failed to send report email: {e}")
        return False


async def send_nurture_email_2(lead_email: str, lead_name: str):
    """
    Email 2: How GR8 AI helps (sent 1 day after report)
    """
    subject = f"{lead_name}, see how others are automating with GR8 AI"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #374151;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .case-study {{
                background: #f0fdfa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background: #0c969b;
                color: white;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            <p>Hi {lead_name},</p>
            
            <p>I hope you found your automation report valuable! I wanted to share a quick example of how businesses like yours are using GR8 AI.</p>
            
            <div class="case-study">
                <h3 style="color: #0c969b; margin-top: 0;">📈 Real Results: SaaS Company</h3>
                <p><strong>Challenge:</strong> Spending 15 hours/week answering repetitive customer questions</p>
                <p><strong>Solution:</strong> Deployed AI Chatbot in 10 minutes</p>
                <p><strong>Results:</strong></p>
                <ul>
                    <li>70% reduction in support tickets</li>
                    <li>24/7 customer support without hiring</li>
                    <li>40% increase in qualified leads</li>
                    <li>Paid for itself in first month</li>
                </ul>
            </div>
            
            <p><strong>The best part?</strong> It took less than 10 minutes to set up. No coding required.</p>
            
            <p>Based on your report, I think you'd see similar results with these automations:</p>
            <ul>
                <li>✓ AI Customer Support (reduce workload by 60-80%)</li>
                <li>✓ Smart Lead Capture (increase conversions by 40%)</li>
                <li>✓ Automated Appointment Booking (save 10+ hours/week)</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="https://gr8ai.com/login" class="button">Start Your Free Trial</a>
            </div>
            
            <p>Have questions about implementing any of these? Reply to this email anytime.</p>
            
            <p>Cheers,<br>
            <strong>The GR8 AI Team</strong></p>
        </div>
    </body>
    </html>
    """
    
    try:
        await send_email(
            to_email=lead_email,
            subject=subject,
            html_content=html_content
        )
        return True
    except EmailDeliveryError as e:
        print(f"Failed to send nurture email 2: {e}")
        return False


async def send_nurture_email_3(lead_email: str, lead_name: str):
    """
    Email 3: Get started free (sent 3 days after report)
    """
    subject = f"Ready to automate, {lead_name}? Start free today"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #374151;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .cta-box {{
                background: linear-gradient(135deg, #0c969b 0%, #0a7a7e 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                text-align: center;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background: white;
                color: #0c969b;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
                font-weight: 600;
            }}
            .feature {{
                display: flex;
                align-items: start;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            <p>Hi {lead_name},</p>
            
            <p>It's been a few days since we sent your automation report. Have you had a chance to review the opportunities we identified?</p>
            
            <p><strong>Here's the thing:</strong> Most businesses wait months to implement automation. Meanwhile, they're losing time, money, and customers every single day.</p>
            
            <div class="cta-box">
                <h2 style="margin-top: 0; color: white;">🎁 Start Free Today</h2>
                <p style="font-size: 16px;">No credit card • No commitment • Full features</p>
                <a href="https://gr8ai.com/login" class="button">Create Free Account</a>
            </div>
            
            <p><strong>What you get instantly:</strong></p>
            <div class="feature">
                <span style="margin-right: 10px;">✓</span>
                <div>
                    <strong>Deploy your first AI agent in under 5 minutes</strong><br/>
                    Our setup wizard guides you step-by-step
                </div>
            </div>
            <div class="feature">
                <span style="margin-right: 10px;">✓</span>
                <div>
                    <strong>Start with our Free plan (no payment required)</strong><br/>
                    Test everything before upgrading
                </div>
            </div>
            <div class="feature">
                <span style="margin-right: 10px;">✓</span>
                <div>
                    <strong>See results within 24 hours</strong><br/>
                    Real ROI from day one
                </div>
            </div>
            
            <p>Don't let your competitors get ahead. The businesses that automate first win.</p>
            
            <p>Ready to transform your business?</p>
            
            <div style="text-align: center;">
                <a href="https://gr8ai.com/login" class="button" style="background: #0c969b; color: white;">Get Started Free →</a>
            </div>
            
            <p>Questions? Reply to this email—I'm happy to help you get started.</p>
            
            <p>To your success,<br>
            <strong>The GR8 AI Team</strong></p>
            
            <p style="font-size: 12px; color: #9ca3af; margin-top: 30px;">
            P.S. Still not sure? Schedule a free 15-minute consultation to discuss your automation needs.
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        await send_email(
            to_email=lead_email,
            subject=subject,
            html_content=html_content
        )
        return True
    except EmailDeliveryError as e:
        print(f"Failed to send nurture email 3: {e}")
        return False


async def schedule_nurture_sequence(db, lead_id: str, lead_email: str, lead_name: str):
    """
    Schedule the full 3-email nurture sequence
    In production, this would use a job queue like Celery
    For now, we'll mark emails as scheduled in database
    """
    nurture_collection = db["email_sequences"]
    
    # Schedule email 2 (1 day later)
    await nurture_collection.insert_one({
        "lead_id": lead_id,
        "email": lead_email,
        "name": lead_name,
        "sequence_number": 2,
        "scheduled_for": datetime.now(timezone.utc) + timedelta(days=1),
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc)
    })
    
    # Schedule email 3 (3 days later)
    await nurture_collection.insert_one({
        "lead_id": lead_id,
        "email": lead_email,
        "name": lead_name,
        "sequence_number": 3,
        "scheduled_for": datetime.now(timezone.utc) + timedelta(days=3),
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc)
    })
    
    print(f"✓ Nurture sequence scheduled for {lead_email}")
