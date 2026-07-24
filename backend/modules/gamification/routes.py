import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.models import User

from modules.gamification.schemas import BadgeResponse, UserBadgeResponse, PointsLogResponse
from modules.gamification import services

router = APIRouter(prefix="/gamification", tags=["gamification"])

@router.get("/badges", response_model=List[UserBadgeResponse])
def get_user_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.get_user_badges(db, current_user.id)

@router.get("/points", response_model=List[PointsLogResponse])
def get_points_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.get_points_history(db, current_user.id)