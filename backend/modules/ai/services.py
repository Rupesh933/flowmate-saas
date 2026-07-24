from groq import Groq
import os
import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from modules.tasks.models import TaskSkipLogs
from modules.ai.models import AiInsights

from core.redis_client import redis_client

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_insight(
    db: Session,
    user_id: uuid.UUID
) -> AiInsights:
    # get skip logs
    skip_logs = db.query(TaskSkipLogs).filter(TaskSkipLogs.user_id==user_id).all()
    print("ai skip_logs: ", skip_logs)

    if not skip_logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No skip log for user {user_id}'
        )
    
    # create a list for skip log
    skip_reason = [log.skip_reason for log in skip_logs]

    # Add new code here to check ai response is in redis cache
    cache_key = f"ai_insight:{user_id}"
    cache_text = redis_client.get(cache_key)

    if cache_text:
        # Find in Redis so skip GROQ AI
        ai_text = cache_text

    else:
        # create prompt
        prompt = f"""
            You are a friendly productivity coach talking directly to a user in a habit-tracking app.

            User's task skip reasons: {skip_reason}
            Total skips: {len(skip_logs)}

            Write ONE short, friendly tip (max 2 lines) to help them stick to their schedule better.

            Rules:
            - Talk directly to the user using "you" — like a friend giving quick advice, not a report.
            - Use simple, everyday words. No jargon, no clinical language (avoid words like "pattern," "analysis," "exhibits," "indicates").
            - Do not describe or repeat their data back to them (don't say things like "you skipped X times because of Y").
            - Be warm and encouraging, not preachy or academic.
            - Output ONLY the tip. No greeting, no explanation, no extra text.

            Example of the tone you should use:
            "Try setting a smaller goal for tired days — even 5 minutes counts!"
            "Maybe move your task to mornings when you're less likely to feel overwhelmed."
            """

        # Call the Groq
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5,
            )

            ai_text = response.choices[0].message.content
            if not ai_text or not ai_text.strip():
                raise HTTPException(status_code=502, detail="AI service returned empty response")
            
            # Cache Result in Redis
            redis_client.setex(cache_key, 3600, ai_text)
        
        except Exception as e:
            print(f"Groq API error for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # save into the database
    new_insight = AiInsights(
        user_id=user_id,
        pattern_type="skip_pattern",
        suggestion=ai_text,
        confidence=0.75,    # for this it is fixed
    )
    db.add(new_insight)
    db.commit()
    db.refresh(new_insight)
    return new_insight

def get_insights(
    db: Session,
    user_id: uuid.UUID
) -> List[AiInsights]:
    return(
        db.query(AiInsights)
        .filter(AiInsights.user_id==user_id)
        .all()
    )