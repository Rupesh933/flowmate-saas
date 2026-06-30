from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from modules.auth.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from modules.auth import services

router = APIRouter(prefix="/auth", tags=['Authentication'])

@router.post('/signup', response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = services.create_user(db, user_data)
    return new_user

@router.post('/login', response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = services.authenticated_user(db,login_data)
    token = services.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}