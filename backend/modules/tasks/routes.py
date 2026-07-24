import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.models import User
from modules.tasks.models import Task
from modules.tasks.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskSkipRequest, TaskSkipLogResponse
from modules.tasks import services

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.create_task(db, task_data, current_user.id)

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.get_all_task(db, current_user.id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.update_task(db, task_id, task_data, current_user.id)

@router.delete("/{task_id}", status_code=200)
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.delete_task(db, current_user.id, task_id)


@router.post("/{task_id}/skip", response_model=TaskSkipLogResponse)
def skip_task(
    task_id: uuid.UUID,
    skip_data: TaskSkipRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.skip_task(db, task_id, current_user.id, skip_data)

@router.get("/skip_patterns")
def get_skip_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("Route called")
    print("task_id =")
    print("user =", current_user)
    return services.get_skip_pattern(db, current_user.id)