import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date

from modules.habits.models import Habit, HabitLog
from modules.habits.schemas import HabitCreate, HabitResponse, HabitLogRequest, HabitLogResponse

def create_habit(
    db: Session,
    habit_data: HabitCreate,
    user_id: uuid.UUID
) -> Habit:
    new_habit = Habit(
        user_id = user_id,
        name = habit_data.name,
        frequency = habit_data.frequency,
        preferred_time = habit_data.preferred_time
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

def get_all_habits(
    db: Session,
    user_id: uuid.UUID
) -> Habit:
    return(
        db.query(Habit)
        .filter(Habit.user_id == user_id)
        .order_by(Habit.is_active == True)
        .all()
    )

def log_habit(
    db: Session,
    user_id: uuid.UUID,
    habit_id: uuid.UUID,
    log_data: HabitLogRequest
):
    # check Habit is exists or that Habit is your
    habit = db.query(Habit).filter(Habit.id==habit_id, Habit.user_id==user_id).first()

    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Habit is not found or this habit is not yours'
        )
    
    # check today's log is already exists
    existing_log = db.query(HabitLog).filter(HabitLog.habit_id==habit_id,HabitLog.log_date == log_data.log_date).first()

    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='A log already exists for this date'
        )
    
    # create log
    habit_log  = HabitLog(
        habit_id = habit_id,
        user_id = user_id,
        log_date=log_data.log_date,
        completed=log_data.completed,
        skip_reason=log_data.skip_reason
    )
    db.add(habit_log)

    # Streak update (only if completed)
    if log_data.completed:
        habit.streak_count += 1
        habit.total_points += 10   # for each log 10 points

        from modules.gamification.services import add_points
        add_points(
            db=db,
            user_id=user_id,
            points=10,
            reason="Habit log Completed",
            source_type="habit"
        )

        # update the longest streak
        if habit.streak_count > habit.longest_streak:
            habit.longest_streak = habit.streak_count
    else:
        # if user miss streak --> streak reset
        habit.streak_count = 0

    db.commit()
    db.refresh(habit_log)
    return habit_log

def delete_habit(
    db: Session,
    habit_id: uuid.UUID,
    user_id: uuid.UUID
) -> dict:
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id==user_id
    ).first()

    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Habit not found'
        )
    
    # No hard delete -- only is_active = False
    habit.is_active = False
    db.commit()
    return {"message": "Habit is closed"}