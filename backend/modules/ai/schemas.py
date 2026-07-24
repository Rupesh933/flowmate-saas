import uuid
from pydantic import BaseModel
from datetime import datetime

class AiInsightResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    pattern_type: str
    suggestion: str
    confidence: float
    is_read: bool
    generated_at: datetime

    class Config:
        from_attributes=True