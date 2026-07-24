import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import uuid

from modules.tasks.models import Task, TaskSkipLogs
from modules.tasks.schemas import TaskCreate, TaskUpdate, TaskSkipRequest, TaskSkipLogResponse

from modules.gamification.services import add_points

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

def update_task(db: Session, task_id: uuid.UUID, task_data: TaskUpdate, user_id: uuid.UUID,) -> Task:
    # find only this user
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    print("Task Data", task_data)

    if not task:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail='Task is not found or Your task is not register'
        )
    
    # only update that field which is shared
    update_data = task_data.model_dump(exclude_unset=True)
    print("Update Date: ", update_data)

    # if you set status is done --> set completed_at
    if update_data.get("status") == "done":
        update_data['completed_at'] = datetime.now()

        # when status is done call add_points()
        # why we call add_function here? reason is give reward 
        add_points(
            db=db,
            user_id=user_id,
            points=10,
            reason="Task Completed",
            source_type="task"
        )
    
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
    
    db.delete(task)
    db.commit()
    return {
        'message': 'Task deleted successfully'
    }


# skip task logs
def skip_task(
    db: Session,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    skip_data: TaskSkipRequest
) -> TaskSkipLogs:
    print("Service started")
    # check task is exist or and that task is yours
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

    print(task)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task is not found or This task is not yours"
        )
    
    # Skipped task status
    task.status = "skipped"
    print(task.status)
    db.commit()

    # make skip log record
    skip_log = TaskSkipLogs(
        task_id=task_id,
        user_id=user_id,
        skip_reason=skip_data.skip_reason,
    )
    db.add(skip_log)
    db.commit()
    db.refresh(skip_log)

    return skip_log

def get_skip_pattern(
    db: Session,
    user_id: uuid.UUID
) -> dict:

    # get user skip patterns - for AI
    logs = db.query(TaskSkipLogs).filter(TaskSkipLogs.user_id == user_id).all()

    # Count Reason
    reasons = {}
    for log in logs:
        reasons[log.skip_reason] = reasons.get(log.skip_reason, 0) +1
    
    return {
        "total_skips": len(logs),
        "reasons": reasons
    }
