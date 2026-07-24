from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from modules.reminders.models import Reminder
from modules.auth.models import User
from core.database import get_db, SessionLocal

IST = timezone(timedelta(hours=5, minutes=30))  # we tell python, (5 hours and 30 minutes) this timezone is fast from UTC(Coordinated Universal Time)
scheduler = AsyncIOScheduler()

async def check_reminders():
    db: Session = SessionLocal()
    try:
        # now = datetime.now().time()
        now = datetime.now(IST).time()

        due_reminder = db.query(Reminder).filter(Reminder.remind_at <= now, Reminder.is_sent==False).all()

        if not due_reminder:
            print(f"[{now}] No due reminders")
            return 
        
        for reminder in due_reminder:
            print(f'🔔 Reminder: Task {reminder.task_id} - remind_at={reminder.remind_at}')
            reminder.is_sent=True
        db.commit()
        
    except Exception as e:
        print(f"[Scheduler Error] {e}")
        db.rollback()
    
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            check_reminders,
            "interval",
            minutes=1,
            id="check_reminder_job",
            replace_existing=True   # protect from duplicate job
        )
        scheduler.start()
        print("[Scheduler] ✅ Started - checking reminders every 1 minute")