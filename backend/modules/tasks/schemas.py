import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime

# Task banane ke liye (Request)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 3
    category: Optional[str] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None

# Task update karne ke liye (request)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    category: Optional[str] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None

# Response (user ko wapas bhejenge)
class TaskResponse(BaseModel):
    id: uuid.UUID = Field(examples=["f81d4fae-7dec-11d0-a765-00a0c91e6bf6"])
    user_id: uuid.UUID = Field(examples=["bcc73f48-7bfc-4ed1-b199-7ec0ad177f44"])
    title: str
    description: Optional[str]
    status: str
    priority: int
    category: Optional[str]
    scheduled_time: Optional[time]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# skip request schema
class TaskSkipRequest(BaseModel):
    skip_reason: str    # "distracted" / "tired" / "forgot"

# Skip log response
class TaskSkipLogResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    skip_reason: str
    skipped_at: datetime

    class Config:
        from_attributes = True