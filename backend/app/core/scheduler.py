# ============================================
# SCHEDULER - Background Task Scheduling
# ============================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.services import EmailProcessor


# Global scheduler instance
scheduler = AsyncIOScheduler()


async def process_daily_emails():
    """
    Scheduled task to fetch and process emails from last 24 hours.
    Runs every 2 minutes to continuously monitor for SAP-related emails.
    Uses mock data in scheduler (real emails require user authentication).
    """
    print(f"[Scheduler] Starting email processing at {datetime.utcnow()}")
    print("[Scheduler] Processing emails from last 24 hours (mock data)")

    # Ensure database is initialized
    try:
        await init_db()
        print("[Scheduler] Database initialized")
    except Exception as e:
        print(f"[Scheduler] Database initialization failed: {e}")
        return

    async with AsyncSessionLocal() as db:
        try:
            # Scheduler always uses mock services (no user tokens available)
            processor = EmailProcessor(db)

            # Process emails from last 24 hours, every 2 minutes
            result = await processor.process_daily_emails(
                days_back=1,  # 24 hours
                max_emails=20,  # Reasonable limit for frequent processing
                auto_create_tickets=True
            )

            await db.commit()

            print(f"[Scheduler] Email processing completed: {result}")
            if result.get('tickets_created', 0) > 0:
                print(f"[Scheduler] ✅ Created {result['tickets_created']} new tickets")

        except Exception as e:
            await db.rollback()
            print(f"[Scheduler] Error: {e}")


async def health_check():
    """
    Periodic health check task.
    """
    print(f"[Scheduler] Health check at {datetime.utcnow()}")


def start_scheduler():
    """
    Scheduler disabled - real email processing requires user authentication.
    Use manual triggers from the frontend instead.
    """
    print("[Scheduler] Disabled - real email processing requires user authentication")
    print("[Scheduler] Use manual triggers from the frontend instead")
    return


def stop_scheduler():
    """
    Stop the background scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] Stopped")


def get_scheduler_status():
    """
    Get current scheduler status and jobs.
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None
        })
    
    return {
        "running": scheduler.running,
        "jobs": jobs
    }


async def trigger_email_processing_now():
    """
    Manually trigger email processing outside of schedule.
    """
    await process_daily_emails()
