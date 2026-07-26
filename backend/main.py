from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.database import engine, Base

from modules.auth.models import User
from modules.auth.routes import router as auth_router

from modules.tasks.models import Task, TaskSkipLogs
from modules.tasks.routes import router as task_router

from modules.habits.models import Habit, HabitLog
from modules.habits.routes import router as habit_router

from modules.reminders.models import Reminder
from modules.reminders.routes import router as reminder_router
from modules.reminders.scheduler import start_scheduler, scheduler

from modules.ai.models import AiInsights
from modules.ai.routes import router as ai_router

from modules.gamification.models import Badge, UserBadges, PointsLog
from modules.gamification.routes import router as gaminfication_router

from modules.payments.models import PaymentLog, Subscription
from modules.payments.routes import router as payment_router

import os
from fastapi.middleware.cors import CORSMiddleware

from core.email_service import send_email

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    start_scheduler()

    yield

    # shutdown
    scheduler.shutdown()

app = FastAPI(
    title="FlowMate SaaS API",
    version="1.0.0",
    description="Productivity SaaS backend",
    lifespan=lifespan
)

# CORS SETUP
allowed_arigins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_arigins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)


# create all table which is inherit from Base
# Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(habit_router)
app.include_router(reminder_router)
app.include_router(ai_router)
app.include_router(gaminfication_router)
app.include_router(payment_router)

from core.redis_client import redis_client
@app.get("/redis_check")
def check_redis():
    try:
        redis_client.set("test_key", "Hello Redis")
        value = redis_client.get("test_key")
        return {"redis": "Connected", "value": value}
    except Exception as e:
        return {"redis": "Failed", "error": str(e)}

# Test Email API
# @app.get("/test-email")
# def test_email():
#     result = send_email(
#         to_email=os.getenv("EMAIL_ADDRESS"),
#         subject="FlowMate test Email",
#         body="This is Test email from FlowMate API"
#     )

#     if result:
#         return {"message": "Test email sent successfully"}
#     else:
#         return {"message": "Email sending failed. Check logs!"}

@app.get("/")
def root():
    return {"status": "ok", "message": "FlowMate API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/db_check")
def check_database():
    try:
        connection = engine.connect()
        connection.close()
        return {
            "database": "Connection successfully connect!"
        }
    except Exception as e:
        return {
            'datbase': "connection failed"
        }