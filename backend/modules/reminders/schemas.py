import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import time, datetime

class ReminderCreate(BaseModel):
    task_id: uuid.UUID
    remind_at: time
    channel: Optional[str] = "app"

    class Config:
        json_schema_extra = {
            "example":{
                "task_id": "past-a-real-uuid-here",
                "remind_at": "09:00:00",
                "channel": "app"
            }
        }

class ReminderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    task_id: uuid.UUID
    remind_at: time
    channel: str
    is_sent: bool
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes=True
    