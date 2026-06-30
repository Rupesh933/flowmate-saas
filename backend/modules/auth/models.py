# In modules/auth/models.py:

# Create a Python version of the users table.

# When Docker restarts, SQLAlchemy will automatically create the "users" table in PostgreSQL!

from sqlalchemy import Boolean
import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email=Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    plan = Column(String, default="Free")
    timezone = Column(String, default='Asia/Kolkata')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())