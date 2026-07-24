import uuid
from pydantic import BaseModel
from datetime import datetime

class BadgeResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    badge_type: str
    required_points: int

    class Config:
        from_attributes=True

class UserBadgeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    badge_id: uuid.UUID
    earned_at: datetime

    class Config:
        from_attributes=True

class PointsLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    points: int
    reason: str
    source_type: str
    created_at: datetime

    class Config:
        from_attributes=True