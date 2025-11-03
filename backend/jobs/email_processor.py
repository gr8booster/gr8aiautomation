"""
Background job processor for automated email sequences
Processes scheduled nurture emails
"""
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from services.nurture_service import send_nurture_email_2, send_nurture_email_3

MONGO_URL = os.environ.get('MONGO_URL')

async def process_scheduled_emails():
    """
    Process scheduled nurture emails
    Run this periodically (e.g., every hour via cron)
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["gr8_automation"]
    email_sequences = db["email_sequences"]
    
    # Find emails scheduled for now or earlier
    now = datetime.now(timezone.utc)
    pending_emails = await email_sequences.find({
        "status": "scheduled",
        "scheduled_for": {"$lte": now}
    }).to_list(100)
    
    print(f"Found {len(pending_emails)} emails to send")
    
    for email_task in pending_emails:
        try:
            # Mark as processing
            await email_sequences.update_one(
                {"_id": email_task["_id"]},
                {"$set": {"status": "processing"}}
            )
            
            # Send appropriate email
            if email_task["sequence_number"] == 2:
                success = await send_nurture_email_2(
                    email_task["email"],
                    email_task["name"]
                )
            elif email_task["sequence_number"] == 3:
                success = await send_nurture_email_3(
                    email_task["email"],
                    email_task["name"]
                )
            else:
                success = False
            
            # Update status
            if success:
                await email_sequences.update_one(
                    {"_id": email_task["_id"]},
                    {"$set": {
                        "status": "sent",
                        "sent_at": datetime.now(timezone.utc)
                    }}
                )
                print(f"✓ Sent email {email_task['sequence_number']} to {email_task['email']}")
            else:
                await email_sequences.update_one(
                    {"_id": email_task["_id"]},
                    {"$set": {"status": "failed"}}
                )
                print(f"✗ Failed to send email to {email_task['email']}")
                
        except Exception as e:
            print(f"Error processing email {email_task['_id']}: {e}")
            await email_sequences.update_one(
                {"_id": email_task["_id"]},
                {"$set": {"status": "failed", "error": str(e)}}
            )
    
    client.close()
    return len(pending_emails)


if __name__ == "__main__":
    # Run as standalone job
    asyncio.run(process_scheduled_emails())
