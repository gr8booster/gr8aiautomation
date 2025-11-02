"""
Appointment Scheduler automation service
Handles appointment booking, availability checking, and confirmations
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from .email_service import send_email, EmailDeliveryError

# Business hours configuration (can be customized per website)
DEFAULT_BUSINESS_HOURS = {
    "monday": {"start": "09:00", "end": "17:00", "enabled": True},
    "tuesday": {"start": "09:00", "end": "17:00", "enabled": True},
    "wednesday": {"start": "09:00", "end": "17:00", "enabled": True},
    "thursday": {"start": "09:00", "end": "17:00", "enabled": True},
    "friday": {"start": "09:00", "end": "17:00", "enabled": True},
    "saturday": {"start": "10:00", "end": "14:00", "enabled": False},
    "sunday": {"start": "closed", "end": "closed", "enabled": False}
}

DEFAULT_SLOT_DURATION = 30  # minutes
DEFAULT_BUFFER_TIME = 15  # minutes between appointments

class AppointmentScheduler:
    def __init__(self, db):
        self.db = db
        self.appointments_collection = db["appointments"]
        self.availability_collection = db["availability_settings"]
    
    async def get_availability_settings(self, website_id: str) -> Dict:
        """Get availability settings for a website"""
        settings = await self.availability_collection.find_one({"website_id": website_id})
        if not settings:
            # Return defaults
            return {
                "website_id": website_id,
                "business_hours": DEFAULT_BUSINESS_HOURS,
                "slot_duration": DEFAULT_SLOT_DURATION,
                "buffer_time": DEFAULT_BUFFER_TIME,
                "timezone": "UTC"
            }
        return settings
    
    async def update_availability_settings(
        self, 
        website_id: str, 
        business_hours: Dict,
        slot_duration: int = DEFAULT_SLOT_DURATION,
        buffer_time: int = DEFAULT_BUFFER_TIME,
        timezone: str = "UTC"
    ) -> Dict:
        """Update availability settings for a website"""
        settings = {
            "website_id": website_id,
            "business_hours": business_hours,
            "slot_duration": slot_duration,
            "buffer_time": buffer_time,
            "timezone": timezone,
            "updated_at": datetime.now(timezone=timezone)
        }
        
        await self.availability_collection.update_one(
            {"website_id": website_id},
            {"$set": settings},
            upsert=True
        )
        
        return await self.get_availability_settings(website_id)
    
    async def get_available_slots(
        self, 
        website_id: str, 
        date: datetime,
        duration: Optional[int] = None
    ) -> List[Dict]:
        """
        Get available time slots for a specific date
        
        Args:
            website_id: Website identifier
            date: Date to check availability
            duration: Appointment duration in minutes (uses settings default if not provided)
        
        Returns:
            List of available time slots
        """
        settings = await self.get_availability_settings(website_id)
        slot_duration = duration or settings["slot_duration"]
        buffer_time = settings["buffer_time"]
        
        # Get day of week
        day_name = date.strftime("%A").lower()
        day_settings = settings["business_hours"].get(day_name, {})
        
        if not day_settings.get("enabled"):
            return []
        
        # Parse business hours
        start_time_str = day_settings.get("start")
        end_time_str = day_settings.get("end")
        
        if not start_time_str or not end_time_str or start_time_str == "closed":
            return []
        
        # Create datetime objects for business hours
        start_hour, start_min = map(int, start_time_str.split(":"))
        end_hour, end_min = map(int, end_time_str.split(":"))
        
        current_slot = date.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
        end_time = date.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
        
        # Get existing appointments for this day
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        existing_appointments = await self.appointments_collection.find({
            "website_id": website_id,
            "start_time": {"$gte": day_start, "$lt": day_end},
            "status": {"$in": ["confirmed", "pending"]}
        }).to_list(100)
        
        # Generate available slots
        available_slots = []
        
        while current_slot + timedelta(minutes=slot_duration) <= end_time:
            slot_end = current_slot + timedelta(minutes=slot_duration)
            
            # Check if slot conflicts with existing appointment
            is_available = True
            for appt in existing_appointments:
                appt_end = appt["start_time"] + timedelta(minutes=appt["duration"])
                buffer_end = appt_end + timedelta(minutes=buffer_time)
                
                # Check for overlap
                if (current_slot < buffer_end and slot_end > appt["start_time"]):
                    is_available = False
                    break
            
            # Check if slot is in the past
            if current_slot < datetime.now(timezone.utc):
                is_available = False
            
            if is_available:
                available_slots.append({
                    "start_time": current_slot.isoformat(),
                    "end_time": slot_end.isoformat(),
                    "duration": slot_duration,
                    "available": True
                })
            
            # Move to next slot
            current_slot += timedelta(minutes=slot_duration + buffer_time)
        
        return available_slots
    
    async def book_appointment(
        self,
        website_id: str,
        start_time: datetime,
        duration: int,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Book an appointment
        
        Returns:
            Appointment details with confirmation
        """
        # Check if slot is still available
        slot_end = start_time + timedelta(minutes=duration)
        
        # Check for conflicts
        conflicts = await self.appointments_collection.find({
            "website_id": website_id,
            "start_time": {"$lt": slot_end},
            "status": {"$in": ["confirmed", "pending"]},
            "$expr": {
                "$gt": [
                    {"$add": ["$start_time", {"$multiply": ["$duration", 60000]}]},  # End time
                    start_time
                ]
            }
        }).to_list(10)
        
        if conflicts:
            raise ValueError("Time slot is no longer available")
        
        # Create appointment
        appointment_id = str(uuid.uuid4())
        appointment = {
            "_id": appointment_id,
            "website_id": website_id,
            "start_time": start_time,
            "duration": duration,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "notes": notes,
            "status": "confirmed",
            "created_at": datetime.now(timezone.utc),
            "confirmation_sent": False
        }
        
        await self.appointments_collection.insert_one(appointment)
        
        # Send confirmation email
        try:
            await self._send_confirmation_email(appointment)
            await self.appointments_collection.update_one(
                {"_id": appointment_id},
                {"$set": {"confirmation_sent": True}}
            )
        except EmailDeliveryError as e:
            print(f"Failed to send confirmation email: {e}")
        
        return appointment
    
    async def _send_confirmation_email(self, appointment: Dict):
        """Send appointment confirmation email"""
        start_time = appointment["start_time"]
        formatted_time = start_time.strftime("%A, %B %d, %Y at %I:%M %p")
        
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
                }}
                .content {{
                    background: white;
                    padding: 30px 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .appointment-details {{
                    background: #f9fafb;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    margin: 10px 0;
                    display: flex;
                }}
                .detail-label {{
                    font-weight: 600;
                    width: 120px;
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
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #9ca3af;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✓ Appointment Confirmed</h1>
            </div>
            <div class="content">
                <p>Hi {appointment['customer_name']},</p>
                <p>Your appointment has been successfully confirmed!</p>
                
                <div class="appointment-details">
                    <h3 style="margin-top: 0;">Appointment Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Date & Time:</span>
                        <span>{formatted_time}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Duration:</span>
                        <span>{appointment['duration']} minutes</span>
                    </div>
                    {f'''<div class="detail-row">
                        <span class="detail-label">Notes:</span>
                        <span>{appointment['notes']}</span>
                    </div>''' if appointment.get('notes') else ''}
                </div>
                
                <p>We look forward to meeting with you!</p>
                <p><strong>Need to reschedule?</strong> Please contact us as soon as possible.</p>
            </div>
            <div class="footer">
                <p>Powered by GR8 AI Automation</p>
            </div>
        </body>
        </html>
        """
        
        await send_email(
            to_email=appointment['customer_email'],
            subject="Appointment Confirmation",
            html_content=html_content
        )
    
    async def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> bool:
        """Cancel an appointment"""
        result = await self.appointments_collection.update_one(
            {"_id": appointment_id},
            {"$set": {
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc),
                "cancellation_reason": reason
            }}
        )
        
        return result.modified_count > 0
    
    async def get_appointments(
        self, 
        website_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get appointments for a website"""
        query = {"website_id": website_id}
        
        if start_date or end_date:
            query["start_time"] = {}
            if start_date:
                query["start_time"]["$gte"] = start_date
            if end_date:
                query["start_time"]["$lte"] = end_date
        
        if status:
            query["status"] = status
        
        appointments = await self.appointments_collection.find(query).sort("start_time", 1).to_list(100)
        return appointments
