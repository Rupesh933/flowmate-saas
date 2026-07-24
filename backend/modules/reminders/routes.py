import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.models import User
from modules.reminders.models import Reminder
from modules.reminders.schemas import ReminderCreate, ReminderResponse
from modules.reminders import services

router = APIRouter(prefix='/reminders', tags=['Reminders'])

@router.post('', response_model=ReminderResponse, status_code=201)
def create_reminder(
    reminder_data: ReminderCreate,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.create_reminder(db, reminder_data, current_user.id)

@router.get('', response_model=List[ReminderResponse])
def get_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.get_reminders(db, current_user.id)

@router.delete('/{reminder_id}', status_code=200)
def delete_reminder(
    reminder_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.delete_reminder(db, reminder_id, current_user.id)