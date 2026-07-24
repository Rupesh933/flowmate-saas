import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from modules.reminders.models import Reminder
from modules.reminders.schemas import ReminderCreate, ReminderResponse
from modules.tasks.models import Task

def create_reminder(
    db: Session,
    reminder_data: ReminderCreate,
    user_id: uuid.UUID
) -> Reminder:
    # Validate that the task exists and belongs to the user
    task = db.query(Task).filter(
        Task.id == reminder_data.task_id,
        Task.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{reminder_data.task_id}' not found"
        )
    new_reminder = Reminder(
        user_id=user_id,
        task_id=reminder_data.task_id,
        remind_at=reminder_data.remind_at,
        channel=reminder_data.channel
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    return new_reminder

def get_reminders(
    db: Session,
    user_id: uuid.UUID
) -> list[Reminder]:
    return(
        db.query(Reminder)
        .filter(Reminder.user_id==user_id)
        .order_by(Reminder.remind_at)
        .all()
    )

def delete_reminder(
    db: Session,
    reminder_id: uuid.UUID,
    user_id: uuid.UUID
) -> dict:
    reminder = db.query(Reminder).filter(Reminder.id==reminder_id, Reminder.user_id==user_id).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    db.delete(reminder)
    db.commit()
    return {
        'message': "Reminder deleted successfully"
    }