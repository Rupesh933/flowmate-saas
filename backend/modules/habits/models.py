from datetime import timezone
import uuid
from sqlalchemy import Column, Integer, Boolean, ForeignKey, String, Date, DateTime, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class Habit(Base):

    __tablename__ = 'habits'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)   
    frequency = Column(String, default='daily')    # daily/weekly
    preferred_time = Column(Time, nullable=True)
    streak_count = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HabitLog(Base):

    __tablename__ = 'habit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(UUID(as_uuid=True), ForeignKey('habits.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    completed = Column(Boolean, default=True)
    skip_reason = Column(String, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())