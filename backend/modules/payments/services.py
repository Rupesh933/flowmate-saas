
import razorpay
import os

import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from modules.payments.models import PaymentLog, Subscription
from modules.auth.models import User

razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

def create_order(amount_rupees: int, user_id: str):
    order = razorpay_client.order.create({
        "amount": amount_rupees * 100,   # convert rupees into paise
        "currency": "INR",
        "payment_capture": 1,
        "notes": {
            "user_id": user_id
        }
    })
    return order


def verify_and_save_payment(
    db: Session,
    user_id: uuid.UUID,
    razorpay_payment_id: str,
    amount_paise: int
):
    # create PaymentLogs
    payment_log = PaymentLog(
        user_id=user_id,
        amount_paise=amount_paise,
        razorpay_payment_id=razorpay_payment_id,
        status="success",
    )

    db.add(payment_log)
    db.commit()
    db.refresh(payment_log)

    # Check/Update subscription
    subscription = db.query(Subscription).filter(Subscription.user_id==user_id).first()

    if subscription:
        # update the existing subscription
        subscription.plan_type="pro"
        subscription.status="active"
        subscription.expires_at = datetime.utcnow() + timedelta(days=30)

    else:
        # Create new Subscription
        subscription = Subscription(
            user_id=user_id,
            plan_type="pro",
            status="active",
            expires_at = datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)

    db.commit()

    # Also update user plan into User table
    user = db.query(User).filter(User.id == user_id).first()
    user.plan = "pro"
    db.commit()

    return payment_log

def get_subscription(
    db: Session,
    user_id: uuid.UUID
):
    return db.query(Subscription).filter(Subscription.user_id==user_id).first()