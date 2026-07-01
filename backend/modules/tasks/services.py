import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import uuid

from modules.tasks.models import Task
from modules.tasks.schemas import TaskCreate, TaskUpdate

def create_task(db: Session, task_data: TaskCreate, user_id: uuid.UUID) -> Task:
    new_user = Task(
        user_id = user_id,
        title = task_data.title,
        description = task_data.description,
        priority = task_data.priority,
        category = task_data.category,
        scheduled_time = task_data.scheduled_time,
        due_date = task_data.due_date
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_all_task(db: Session, user_id: uuid.UUID) -> list[Task]:
    print("db: session: ",db)
    print("uuid.UUID: ", user_id)
    return(
        db.query(Task)
        .filter(Task.user_id == user_id)  # ← MULTI-TENANCY!
        .order_by(Task.priority.asc(),Task.created_at.desc())
        .all()
    )

def update_task(db: Session, user_id: uuid.UUID, task_data: TaskUpdate,) -> Task:
    # find only this user
    task = db.query(Task).filter(Task.id == user_id).first()

    if not task:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail='Task is found or Your task is not register'
        )
    
    # only update that field which is shared
    update_data = task_data.model_dump(exclude_unset=True)

    # if you set status is done --> set completed_at
    if update_data.get("status") == "done":
        update_data['completed_at'] = datetime.now()
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> dict:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task is found or not your task'
        )
    
    db.delete()
    db.commit()
    return {
        'message': 'Task deleted successfully'
    }