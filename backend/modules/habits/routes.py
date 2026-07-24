import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from modules.habits.models import Habit, HabitLog
from modules.habits.schemas import HabitCreate, HabitLogRequest, HabitLogResponse, HabitResponse
from modules.habits import services

from core.dependencies import get_current_user
from core.database import get_db
from modules.auth.models import User

router = APIRouter(prefix="/habits", tags=['Habits'])

@router.post('', response_model=HabitResponse)
def create_habit(
    habit_data: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.create_habit(db, habit_data, current_user.id)

@router.get('', response_model=List[HabitResponse])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.get_all_habits(db, current_user.id)

@router.post("/{habit_id}/log", response_model=HabitLogResponse)
def log_habit(
    habit_id: uuid.UUID,
    log_data: HabitLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.log_habit(
        db, current_user.id, habit_id, log_data
    )

@router.delete("/{habit_id}")
def delete_habit(
    db: Session = Depends(get_db),
    habit_id = uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    return services.delete_habit(db, habit_id, current_user.id)