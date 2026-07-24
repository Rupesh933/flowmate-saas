from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from modules.ai.schemas import AiInsightResponse
from modules.ai import services
from core.dependencies import get_current_user
from core.database import get_db
from modules.auth.models import User

router = APIRouter(prefix="/ai", tags=['AI'])

@router.post('/generate', response_model=AiInsightResponse)
def generate_insight(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.generate_insight(db, current_user.id)

@router.get("/insights", response_model=List[AiInsightResponse])
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return services.get_insights(db, current_user.id)