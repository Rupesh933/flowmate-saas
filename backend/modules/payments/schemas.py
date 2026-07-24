import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_type: str
    razorpay_sub_id: Optional[str] = None  # this is nullable for database (so this is optional, may be for free plan it is NULL)
    status: str
    started_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class PaymentLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    subscription_id: Optional[uuid.UUID] = None
    amount_paise: int
    razorpay_payment_id: Optional[str] = None
    status: str
    paid_at: datetime

    class Config:
        from_attributes = True