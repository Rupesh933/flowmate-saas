
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from modules.auth.models import User
from modules.auth.schemas import UserCreate, LoginRequest

import os
from jose import jwt
from datetime import datetime, timedelta, timezone

# make context of Bcrypt - for password hash/verify
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_user(db: Session, user_data: UserCreate) -> User:
    # check email is already exist or not
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="This email account is already exist"
        )
    
    # hash the password
    hashed_password = pwd_context.hash(user_data.password)

    # create object for new user
    new_user = User(
        name = user_data.name,
        email = user_data.email,
        password_hash = hashed_password
    )

    # Save the user in DataBase
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

JWT_SECRET = os.getenv("JWT_SECRET_key", "default_secret_key_change_me_in_production")
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES  = 60 * 24

def authenticated_user(db: Session, login_data: LoginRequest) -> User:
    # find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    print("user email: ",user)

    # Check user does not exist or password is wrong
    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is wrong"
        )
    return user

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),   # 'sub' --> subject, means whos token is it
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
