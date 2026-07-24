
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user

from modules.auth.models import User

from modules.payments import services

router = APIRouter(prefix="/payments", tags=['Payments'])


class CreateOrderRequest(BaseModel):
    amount: int  # in rupees

@router.post("/create-order")
def create_order_route(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_user)
):
    order = services.create_order(order_data.amount, str(current_user.id))
    return order

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        payload = await request.json()
        print("Payload: ", payload)

        # this data is comming from Razorpay
        event = payload.get("event")
        print("Event(This data is comming from Razorpay): ", event)

        if event == "payment.captured":
            payment_entity = payload["payload"]["payment"]["entity"]
            print("Payment_entity: ", payment_entity)

            # get payment details from here
            razorpay_payment_id = payment_entity["id"]
            amount_paise = payment_entity["amount"]
            print("Razorpay Payment id: ", razorpay_payment_id)
            print("Amount paise: ", amount_paise)

            # But where to find user id?
            # this is send in "notes" when we create order
            user_id = payment_entity["notes"]["user_id"]

            services.verify_and_save_payment(
                db,
                user_id,
                razorpay_payment_id,
                amount_paise
            )
        return {"status": "ok"}
    except Exception as e:
        print("Error", str(e))
        return {"Error": str(e)}

@router.get("/subscription")
def get_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    subscription = services.get_subscription(db, current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "No Subscription found. You're on the free plan"
        )
    return subscription