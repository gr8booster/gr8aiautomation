"""
Email delivery service using SendGrid
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@gr8ai.com')
SENDER_NAME = os.environ.get('SENDER_NAME', 'GR8 AI Automation')

class EmailDeliveryError(Exception):
    """Exception raised when email delivery fails"""
    pass

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_text_content: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> bool:
    """
    Send email via SendGrid
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML content of the email
        plain_text_content: Plain text version (optional, will extract from HTML if not provided)
        from_email: Sender email (defaults to SENDER_EMAIL env var)
        from_name: Sender name (defaults to SENDER_NAME env var)
    
    Returns:
        bool: True if email sent successfully
        
    Raises:
        EmailDeliveryError: If email delivery fails
    """
    if not SENDGRID_API_KEY:
        print("Warning: SENDGRID_API_KEY not configured. Email not sent.")
        return False
    
    try:
        from_addr = Email(
            email=from_email or SENDER_EMAIL,
            name=from_name or SENDER_NAME
        )
        to_addr = To(to_email)
        
        # Create email content
        content = Content("text/html", html_content)
        
        # Build the email
        mail = Mail(
            from_email=from_addr,
            to_emails=to_addr,
            subject=subject,
            html_content=content
        )
        
        # Add plain text if provided
        if plain_text_content:
            mail.content = [
                Content("text/plain", plain_text_content),
                content
            ]
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
        
        # SendGrid returns 202 on success
        if response.status_code == 202:
            print(f"Email sent successfully to {to_email}")
            return True
        else:
            print(f"SendGrid returned status {response.status_code}")
            return False
            
    except Exception as e:
        error_msg = f"Failed to send email to {to_email}: {str(e)}"
        print(error_msg)
        raise EmailDeliveryError(error_msg)


async def send_lead_autoresponse_email(
    to_email: str,
    lead_name: str,
    company_name: str,
    autoresponse_content: str
) -> bool:
    """
    Send personalized auto-response email to a lead
    
    Args:
        to_email: Lead's email address
        lead_name: Lead's name
        company_name: Business name
        autoresponse_content: AI-generated response content
    
    Returns:
        bool: True if sent successfully
    """
    subject = f"Thank you for contacting {company_name}!"
    
    # Create HTML email template
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
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .content {{
                background: white;
                padding: 30px 20px;
                border-radius: 0 0 8px 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .greeting {{
                font-size: 16px;
                margin-bottom: 20px;
            }}
            .message {{
                background: #f9fafb;
                padding: 20px;
                border-left: 4px solid #0c969b;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #9ca3af;
                font-size: 14px;
            }}
            .button {{
                display: inline-block;
                background: #0c969b;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✨ {company_name}</h1>
        </div>
        <div class="content">
            <div class="greeting">
                <p>Hi {lead_name},</p>
            </div>
            <div class="message">
                {autoresponse_content.replace(chr(10), '<br>')}
            </div>
            <p>We look forward to connecting with you soon!</p>
        </div>
        <div class="footer">
            <p>This email was sent by {company_name} via GR8 AI Automation</p>
            <p>Powered by AI-driven automation</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_text = f"""
    Hi {lead_name},
    
    {autoresponse_content}
    
    We look forward to connecting with you soon!
    
    ---
    This email was sent by {company_name} via GR8 AI Automation
    """
    
    return await send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        plain_text_content=plain_text
    )
