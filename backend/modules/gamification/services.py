from typing import List
import uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from modules.gamification.models import Badge, UserBadges, PointsLog

def add_points(
    db: Session,
    user_id: uuid.UUID,
    points: int,
    reason: str,
    source_type: str
) -> PointsLog:
    print("gamifictaion services db: ",db)
    print("gamifictaion services user_id: ",user_id)
    print("gamifictaion services points: ",points)
    print("gamifictaion services reason: ",reason)
    print("gamifictaion services source_type: ",source_type)

    new_log = PointsLog(
        user_id=user_id,
        points=points,
        reason=reason,
        source_type=source_type,
    )
    db.add(new_log)
    db.commit()

    # Calculate total points
    total_points = db.query(
        func.sum(PointsLog.points)    # calculate total point for this user
    ).filter(PointsLog.user_id==user_id).scalar()  # scalar means return one single value instead of list
    print("Total Points: ", total_points)

    # check Available badge
    available_badge = db.query(Badge).filter(Badge.required_points <= total_points).all()
    print("Available badge: ", available_badge)

    for badge in available_badge:
        print("For loop Badge: ", badge)
        # check user is already earn
        already_earn = db.query(UserBadges).filter(
            UserBadges.user_id==user_id,
            UserBadges.badge_id==badge.id
        ).first()
        print("Already Earn: ", already_earn)

        if not already_earn:
            # Give new badge
            new_badge = UserBadges(
                user_id=user_id,
                badge_id=badge.id
            )
            db.add(new_badge)
            db.commit()
    return new_log

def get_user_badges(
    db: Session,
    user_id: uuid.UUID
) -> List[UserBadges]:
    return db.query(UserBadges).filter(UserBadges.user_id==user_id).order_by(UserBadges.earned_at).all()

def get_points_history(
    db: Session,
    user_id: uuid.UUID
) -> List[PointsLog]:
    return db.query(PointsLog).filter(PointsLog.user_id==user_id).order_by(PointsLog.created_at).all()

