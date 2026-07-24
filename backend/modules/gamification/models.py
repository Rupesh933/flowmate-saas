import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

# Master List
class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # e.g. "7-Day Warrior"
    description = Column(String, nullable=False)
    badge_type = Column(String, nullable=False)  # streak/completion/time
    required_points = Column(Integer, default=0)

class UserBadges(Base):
    __tablename__ = 'user_badges'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

class PointsLog(Base):
    __tablename__ = 'point_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    points = Column(Integer, default=0)
    reason = Column(String, nullable=False)   # "Task done", "7-day streak"
    source_type = Column(String, nullable=False)    # task/habit/streak
    created_at = Column(DateTime(timezone=True), server_default=func.now())