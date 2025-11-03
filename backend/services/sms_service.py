"""
Twilio SMS notification service
"""
import os
from twilio.rest import Client
from datetime import datetime, timezone

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

class SMSDeliveryError(Exception):
    pass

def get_twilio_client():
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return None
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

async def send_sms(to_number: str, message: str) -> bool:
    """
    Send SMS via Twilio
    """
    client = get_twilio_client()
    if not client:
        print("Warning: Twilio not configured. SMS not sent.")
        return False
    
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"SMS sent to {to_number}: {message.sid}")
        return True
    except Exception as e:
        print(f"SMS send error: {e}")
        raise SMSDeliveryError(f"Failed to send SMS: {str(e)}")

async def send_appointment_reminder_sms(to_number: str, appointment_time: str, business_name: str) -> bool:
    """
    Send appointment reminder SMS
    """
    message = f"Reminder: You have an appointment with {business_name} on {appointment_time}. Reply CONFIRM to confirm."
    return await send_sms(to_number, message)

async def send_lead_alert_sms(to_number: str, lead_name: str, lead_email: str) -> bool:
    """
    Send SMS alert for new lead
    """
    message = f"🔔 New lead captured! {lead_name} ({lead_email}). Check your dashboard for details."
    return await send_sms(to_number, message)
