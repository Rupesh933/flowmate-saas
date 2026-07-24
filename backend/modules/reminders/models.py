import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    remind_at = Column(Time, nullable=False)
    channel = Column(String, default='app')   # app/email/whatsapp
    is_sent = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())