from random import random
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status

from modules.auth.models import User
from modules.auth.schemas import UserCreate, LoginRequest

import os
from jose import jwt
from datetime import datetime, timedelta, timezone

import random
from core.redis_client import redis_client
from core.email_service import send_email

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_user(db: Session, user_data: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email account already exists"
        )

    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{new_user.email}", 600, otp)

    send_email(
        to_email=new_user.email,
        subject="Verify your email account - FlowMate",
        body=f"Your OTP is: {otp}\nThis OTP expires in 10 minutes."
    )

    return new_user


def verify_email_otp(db: Session, email: str, otp: str): 
    stored_otp = redis_client.get(f'otp:{email}')

    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='OTP has expired. Please resend OTP'
        )

    if stored_otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)

    redis_client.delete(f"otp:{email}")

    return user


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 60 * 24


def authenticated_user(db: Session, login_data: LoginRequest) -> User:
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is wrong"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )


    return user


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.email==email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"reset_otp:{email}", 600, otp)

    send_email(
        to_email=user.email,
        subject="Reset your password - FlowMate",
        body=f"Your reset OTP is: {otp}\nThis otp is expire in 10 min."
    )

    return {"message": "OTP send successfully"}

def reset_password(db: Session, email: str, otp: str, new_password: str):
    stored_otp = redis_client.get(f'reset_otp:{email}')

    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP has expired. Please resend otp"
        )
    
    if stored_otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    user = db.query(User).filter(User.email==email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    hashed_new_password = pwd_context.hash(new_password)
    user.password_hash = hashed_new_password
    
    db.commit()
    db.refresh(user)

    redis_client.delete(f"reset_otp:{email}")

    return {"message": "Password reset successfully"}