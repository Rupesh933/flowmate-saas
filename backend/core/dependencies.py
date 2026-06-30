from backend.modules.auth.services import JWT_ALGORITHM
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from core.database import get_db
from modules.auth.models import User

security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_AUTHENTICATION = 'HS256'

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")