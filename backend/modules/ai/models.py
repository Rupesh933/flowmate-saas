import uuid
from sqlalchemy import Column, String, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class AiInsights(Base):
    __tablename__ = 'ai_insights'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pattern_type = Column(String, nullable=False)  # which type of thing find by ai
    suggestion = Column(String, nullable=False)  # actuall text message of ai
    confidence  = Column(Float, nullable=False)  # how sure are ai about this suggesion
    is_read = Column(Boolean, default=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())