"""
Seed Script - Populate all tables with sample data for user: Kilton
Run: python seed_data.py  (from the backend directory)
"""

import uuid
import os
from datetime import datetime, date, time, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core.database import engine, SessionLocal, Base
from modules.auth.models import User
from modules.tasks.models import Task, TaskSkipLogs
from modules.habits.models import Habit, HabitLog
from modules.reminders.models import Reminder
from modules.gamification.models import Badge, UserBadges, PointsLog
from modules.ai.models import AiInsights

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# ─── Fixed UUIDs (so foreign keys reference correctly) ──────────────────────
USER_ID = uuid.uuid4()

TASK_IDS = [uuid.uuid4() for _ in range(7)]
HABIT_IDS = [uuid.uuid4() for _ in range(6)]
BADGE_IDS = [uuid.uuid4() for _ in range(7)]

# ─── Base timestamps ────────────────────────────────────────────────────────
NOW = datetime.now(timezone.utc)
TODAY = date.today()


def seed():
    db: Session = SessionLocal()
    try:
        # ────────────────────────────────────────────────────────────────
        # Check if user already exists
        # ────────────────────────────────────────────────────────────────
        existing = db.query(User).filter(User.email == "kilton@example.com").first()
        if existing:
            print("⚠️  User 'kilton@example.com' already exists. Skipping seed.")
            print(f"   Existing User ID: {existing.id}")
            return

        # ════════════════════════════════════════════════════════════════
        # 1. USERS TABLE  (1 record - the new user)
        # ════════════════════════════════════════════════════════════════
        hashed_pw = pwd_context.hash("Kilton2026")
        user = User(
            id=USER_ID,
            name="Kilton",
            email="kilton@example.com",
            password_hash=hashed_pw,
            plan="Free",
            timezone="Asia/Kolkata",
            is_active=True,
        )
        db.add(user)
        db.flush()  # get the user ID available for FK references
        print(f"✅ User created  →  id: {USER_ID}")

        # ════════════════════════════════════════════════════════════════
        # 2. TASKS TABLE  (7 records)
        # ════════════════════════════════════════════════════════════════
        tasks_data = [
            {
                "id": TASK_IDS[0],
                "title": "Complete project proposal",
                "description": "Draft and finalize the Q3 project proposal document",
                "status": "done",
                "priority": 1,
                "category": "Work",
                "scheduled_time": time(9, 0),
                "due_date": TODAY - timedelta(days=2),
                "completed_at": NOW - timedelta(days=2, hours=3),
            },
            {
                "id": TASK_IDS[1],
                "title": "Morning workout routine",
                "description": "30 min cardio + 20 min strength training",
                "status": "done",
                "priority": 2,
                "category": "Health",
                "scheduled_time": time(6, 30),
                "due_date": TODAY - timedelta(days=1),
                "completed_at": NOW - timedelta(days=1, hours=5),
            },
            {
                "id": TASK_IDS[2],
                "title": "Read chapter 5 of Deep Work",
                "description": "Focus on the section about deliberate practice",
                "status": "done",
                "priority": 3,
                "category": "Learning",
                "scheduled_time": time(20, 0),
                "due_date": TODAY - timedelta(days=1),
                "completed_at": NOW - timedelta(days=1, hours=1),
            },
            {
                "id": TASK_IDS[3],
                "title": "Grocery shopping",
                "description": "Buy vegetables, fruits, and weekly essentials",
                "status": "pending",
                "priority": 3,
                "category": "Personal",
                "scheduled_time": time(17, 0),
                "due_date": TODAY,
                "completed_at": None,
            },
            {
                "id": TASK_IDS[4],
                "title": "Review pull requests",
                "description": "Review and approve pending PRs on the main repository",
                "status": "pending",
                "priority": 1,
                "category": "Work",
                "scheduled_time": time(11, 0),
                "due_date": TODAY,
                "completed_at": None,
            },
            {
                "id": TASK_IDS[5],
                "title": "Plan weekend trip",
                "description": "Research destinations and book accommodation",
                "status": "skipped",
                "priority": 4,
                "category": "Personal",
                "scheduled_time": time(19, 0),
                "due_date": TODAY - timedelta(days=3),
                "completed_at": None,
            },
            {
                "id": TASK_IDS[6],
                "title": "Write blog post on FastAPI",
                "description": "Cover authentication and middleware patterns",
                "status": "pending",
                "priority": 2,
                "category": "Learning",
                "scheduled_time": time(14, 0),
                "due_date": TODAY + timedelta(days=2),
                "completed_at": None,
            },
        ]

        for t in tasks_data:
            db.add(Task(user_id=USER_ID, **t))
        db.flush()  # flush tasks before reminders/skip_logs reference them
        print(f"✅ Tasks created  →  {len(tasks_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 3. TASK_SKIP_LOGS TABLE  (5 records)
        # ════════════════════════════════════════════════════════════════
        skip_logs_data = [
            {"task_id": TASK_IDS[5], "skip_reason": "Feeling unwell, postponing trip planning"},
            {"task_id": TASK_IDS[3], "skip_reason": "Heavy rain, will shop tomorrow"},
            {"task_id": TASK_IDS[4], "skip_reason": "Waiting for teammates to push final changes"},
            {"task_id": TASK_IDS[6], "skip_reason": "Need more research before writing"},
            {"task_id": TASK_IDS[5], "skip_reason": "Budget not finalized yet"},
        ]

        for i, sl in enumerate(skip_logs_data):
            db.add(TaskSkipLogs(
                id=uuid.uuid4(),
                user_id=USER_ID,
                skip_reason=sl["skip_reason"],
                task_id=sl["task_id"],
            ))
        print(f"✅ Task skip logs created  →  {len(skip_logs_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 4. HABITS TABLE  (6 records)
        # ════════════════════════════════════════════════════════════════
        habits_data = [
            {
                "id": HABIT_IDS[0],
                "name": "Morning Meditation",
                "frequency": "daily",
                "preferred_time": time(6, 0),
                "streak_count": 12,
                "longest_streak": 15,
                "total_points": 120,
                "is_active": True,
            },
            {
                "id": HABIT_IDS[1],
                "name": "Drink 8 Glasses of Water",
                "frequency": "daily",
                "preferred_time": time(8, 0),
                "streak_count": 7,
                "longest_streak": 21,
                "total_points": 70,
                "is_active": True,
            },
            {
                "id": HABIT_IDS[2],
                "name": "Read for 30 Minutes",
                "frequency": "daily",
                "preferred_time": time(21, 0),
                "streak_count": 5,
                "longest_streak": 10,
                "total_points": 50,
                "is_active": True,
            },
            {
                "id": HABIT_IDS[3],
                "name": "Weekly Gym Session",
                "frequency": "weekly",
                "preferred_time": time(7, 0),
                "streak_count": 4,
                "longest_streak": 8,
                "total_points": 80,
                "is_active": True,
            },
            {
                "id": HABIT_IDS[4],
                "name": "Journal Before Bed",
                "frequency": "daily",
                "preferred_time": time(22, 0),
                "streak_count": 3,
                "longest_streak": 14,
                "total_points": 30,
                "is_active": True,
            },
            {
                "id": HABIT_IDS[5],
                "name": "No Social Media Before Noon",
                "frequency": "daily",
                "preferred_time": time(12, 0),
                "streak_count": 0,
                "longest_streak": 5,
                "total_points": 20,
                "is_active": False,
            },
        ]

        for h in habits_data:
            db.add(Habit(user_id=USER_ID, **h))
        db.flush()  # flush habits before habit_logs reference them
        print(f"✅ Habits created  →  {len(habits_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 5. HABIT_LOGS TABLE  (7 records)
        # ════════════════════════════════════════════════════════════════
        habit_logs_data = [
            {"habit_id": HABIT_IDS[0], "log_date": TODAY - timedelta(days=1), "completed": True,  "skip_reason": None},
            {"habit_id": HABIT_IDS[0], "log_date": TODAY,                     "completed": True,  "skip_reason": None},
            {"habit_id": HABIT_IDS[1], "log_date": TODAY - timedelta(days=1), "completed": True,  "skip_reason": None},
            {"habit_id": HABIT_IDS[1], "log_date": TODAY,                     "completed": False, "skip_reason": "Forgot to track today"},
            {"habit_id": HABIT_IDS[2], "log_date": TODAY - timedelta(days=2), "completed": True,  "skip_reason": None},
            {"habit_id": HABIT_IDS[3], "log_date": TODAY - timedelta(days=5), "completed": True,  "skip_reason": None},
            {"habit_id": HABIT_IDS[4], "log_date": TODAY - timedelta(days=1), "completed": False, "skip_reason": "Too tired after late meeting"},
        ]

        for hl in habit_logs_data:
            db.add(HabitLog(
                id=uuid.uuid4(),
                user_id=USER_ID,
                **hl,
            ))
        print(f"✅ Habit logs created  →  {len(habit_logs_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 6. REMINDERS TABLE  (6 records)
        # ════════════════════════════════════════════════════════════════
        reminders_data = [
            {"task_id": TASK_IDS[3], "remind_at": time(16, 30), "channel": "app",      "is_sent": False, "retry_count": 0},
            {"task_id": TASK_IDS[4], "remind_at": time(10, 45), "channel": "email",    "is_sent": False, "retry_count": 0},
            {"task_id": TASK_IDS[0], "remind_at": time(8, 30),  "channel": "app",      "is_sent": True,  "retry_count": 0},
            {"task_id": TASK_IDS[1], "remind_at": time(6, 15),  "channel": "whatsapp", "is_sent": True,  "retry_count": 1},
            {"task_id": TASK_IDS[6], "remind_at": time(13, 30), "channel": "email",    "is_sent": False, "retry_count": 0},
            {"task_id": TASK_IDS[2], "remind_at": time(19, 45), "channel": "app",      "is_sent": True,  "retry_count": 2},
        ]

        for r in reminders_data:
            db.add(Reminder(
                id=uuid.uuid4(),
                user_id=USER_ID,
                **r,
            ))
        print(f"✅ Reminders created  →  {len(reminders_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 7. BADGES TABLE  (7 records — master/global data)
        # ════════════════════════════════════════════════════════════════
        badges_data = [
            {"id": BADGE_IDS[0], "name": "7-Day Warrior",       "description": "Complete a 7-day streak on any habit",       "badge_type": "streak",     "required_points": 70},
            {"id": BADGE_IDS[1], "name": "14-Day Champion",     "description": "Maintain a 14-day streak on any habit",      "badge_type": "streak",     "required_points": 140},
            {"id": BADGE_IDS[2], "name": "Task Crusher",        "description": "Complete 10 tasks in a single week",         "badge_type": "completion", "required_points": 100},
            {"id": BADGE_IDS[3], "name": "Early Bird",          "description": "Complete 5 tasks before 9 AM",               "badge_type": "time",       "required_points": 50},
            {"id": BADGE_IDS[4], "name": "Habit Master",        "description": "Reach a 30-day streak on any habit",         "badge_type": "streak",     "required_points": 300},
            {"id": BADGE_IDS[5], "name": "Consistency King",    "description": "Log habits for 21 consecutive days",         "badge_type": "streak",     "required_points": 210},
            {"id": BADGE_IDS[6], "name": "First Step",          "description": "Complete your very first task",              "badge_type": "completion", "required_points": 10},
        ]

        for b in badges_data:
            db.add(Badge(**b))
        db.flush()  # flush badges before user_badges reference them
        print(f"✅ Badges created  →  {len(badges_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 8. USER_BADGES TABLE  (5 records — badges earned by Kilton)
        # ════════════════════════════════════════════════════════════════
        user_badges_data = [
            {"badge_id": BADGE_IDS[6], "earned_at": NOW - timedelta(days=20)},   # First Step
            {"badge_id": BADGE_IDS[0], "earned_at": NOW - timedelta(days=10)},   # 7-Day Warrior
            {"badge_id": BADGE_IDS[3], "earned_at": NOW - timedelta(days=7)},    # Early Bird
            {"badge_id": BADGE_IDS[2], "earned_at": NOW - timedelta(days=3)},    # Task Crusher
            {"badge_id": BADGE_IDS[1], "earned_at": NOW - timedelta(days=1)},    # 14-Day Champion
        ]

        for ub in user_badges_data:
            db.add(UserBadges(
                id=uuid.uuid4(),
                user_id=USER_ID,
                **ub,
            ))
        print(f"✅ User badges created  →  {len(user_badges_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 9. POINT_LOGS TABLE  (7 records)
        # ════════════════════════════════════════════════════════════════
        points_data = [
            {"points": 10, "reason": "First task completed",           "source_type": "task",   "created_at": NOW - timedelta(days=20)},
            {"points": 10, "reason": "Task done - Morning workout",    "source_type": "task",   "created_at": NOW - timedelta(days=15)},
            {"points": 10, "reason": "Habit logged - Meditation",      "source_type": "habit",  "created_at": NOW - timedelta(days=12)},
            {"points": 70, "reason": "7-day streak on Meditation",     "source_type": "streak", "created_at": NOW - timedelta(days=10)},
            {"points": 50, "reason": "5 tasks before 9 AM",            "source_type": "task",   "created_at": NOW - timedelta(days=7)},
            {"points": 100,"reason": "10 tasks in a week",             "source_type": "task",   "created_at": NOW - timedelta(days=3)},
            {"points": 140,"reason": "14-day streak on Meditation",    "source_type": "streak", "created_at": NOW - timedelta(days=1)},
        ]

        for p in points_data:
            created = p.pop("created_at")
            db.add(PointsLog(
                id=uuid.uuid4(),
                user_id=USER_ID,
                **p,
            ))
        print(f"✅ Point logs created  →  {len(points_data)} records")

        # ════════════════════════════════════════════════════════════════
        # 10. AI_INSIGHTS TABLE  (5 records)
        # ════════════════════════════════════════════════════════════════
        insights_data = [
            {
                "pattern_type": "productivity_peak",
                "suggestion": "You are most productive between 9 AM and 11 AM. Try scheduling important tasks during this window.",
                "confidence": 0.87,
                "is_read": True,
            },
            {
                "pattern_type": "habit_consistency",
                "suggestion": "Your meditation streak is strong! Consider increasing session duration to 15 minutes for deeper focus.",
                "confidence": 0.92,
                "is_read": True,
            },
            {
                "pattern_type": "task_completion",
                "suggestion": "You tend to skip tasks on Fridays. Consider reducing your Friday workload or scheduling lighter tasks.",
                "confidence": 0.78,
                "is_read": False,
            },
            {
                "pattern_type": "energy_pattern",
                "suggestion": "Your workout completion rate drops when you schedule it after 5 PM. Morning workouts show 90% completion.",
                "confidence": 0.85,
                "is_read": False,
            },
            {
                "pattern_type": "streak_warning",
                "suggestion": "Your 'No Social Media Before Noon' habit has broken its streak. Restart it to build momentum again.",
                "confidence": 0.95,
                "is_read": False,
            },
        ]

        for ai in insights_data:
            db.add(AiInsights(
                id=uuid.uuid4(),
                user_id=USER_ID,
                **ai,
            ))
        print(f"✅ AI insights created  →  {len(insights_data)} records")

        # ────────────────────────────────────────────────────────────────
        # COMMIT everything
        # ────────────────────────────────────────────────────────────────
        db.commit()
        print("\n🎉 All seed data committed successfully!")
        print(f"   User: Kilton  |  Email: kilton@example.com  |  Password: Kilton2026")
        print(f"   User ID: {USER_ID}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
