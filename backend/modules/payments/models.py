import uuid
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_type = Column(String, default="free")  # free/pro
    razorpay_sub_id = Column(String, nullable=True)
    status = Column(String, default="active")   # active/cancelled/expired
    started_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class PaymentLog(Base):
    __tablename__ = "payments_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    amount_paise = Column(Integer, default=0)  # Razorpay work with paise intead of rupees
    razorpay_payment_id = Column(String, nullable=True)
    status = Column(String, default="pending")  # success/failed/pending
    paid_at = Column(DateTime(timezone=True), default=func.now())