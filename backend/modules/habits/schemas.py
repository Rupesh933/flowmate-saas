import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class HabitCreate(BaseModel):
    name: str
    frequency: Optional[str] = 'daily'
    preferred_time: Optional[time] = None

class HabitResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    frequency: str
    preferred_time: Optional[time]
    streak_count: int
    longest_streak: int
    total_points: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class HabitLogRequest(BaseModel):
    log_date: date
    completed: bool
    skip_reason: Optional[str] = None

class HabitLogResponse(BaseModel):
    id: uuid.UUID
    habit_id: uuid.UUID
    log_date: date
    completed: bool
    skip_reason: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True