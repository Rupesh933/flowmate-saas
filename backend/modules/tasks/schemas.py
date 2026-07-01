import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

# Task banane ke liye (Request)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 3
    category: Optional[str] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[time] = None

# Task update karne ke liye (request)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[time] = None

# Response (user ko wapas bhejenge)
class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    category: Optional[str]
    scheduled_time: Optional[time]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
