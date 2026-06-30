
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from modules.auth.models import User
from modules.auth.schemas import UserCreate

# make context of Bcrypt - for password hash/verify
pwd_context = CryptContext(schema=['bcrypt'], deprecated='auto')

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
        password_hash = user_data.password
    )

    # Save the user in DataBase
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user