import uuid
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from datetime import datetime, timezone, timedelta
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")  # pendding/done/skipped
    priority = Column(String, default=3)     # 1=High, 5=Low
    category = Column(String, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())