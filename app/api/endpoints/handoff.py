from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from uuid import uuid4
from datetime import datetime
from app import models, db
from pydantic import BaseModel
from typing import List, Optional
import requests

router = APIRouter()

class HandoffRequest(BaseModel):
    external_session_id: str
    question_text: str
    answer_type: str
    persona: str
    possible_answers: Optional[List[str]] = None

@router.post("/")
def handoff(
    handoff_in: HandoffRequest,
    db_session: DBSession = Depends(db.get_db)
):
    # Find a user matching the persona
    user = db_session.query(models.User).filter_by(persona=handoff_in.persona).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user found for persona")
    # Create session
    session_obj = models.Session(
        id=uuid4(),
        user_id=user.id,
        current_step=0,
        status="active",
        external_session_id=handoff_in.external_session_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(session_obj)
    db_session.flush()  # get session_obj.id
    # Create question
    question_obj = models.Question(
        question_text=handoff_in.question_text,
        answer_type=handoff_in.answer_type,
        possible_answers=handoff_in.possible_answers,
        created_at=datetime.utcnow()
    )
    db_session.add(question_obj)
    db_session.flush()  # get question_obj.id
    # Pick preferred channel for user (if any)
    user_channel = next((uc for uc in user.user_channels if uc.is_preferred), None)
    if not user_channel:
        raise HTTPException(status_code=400, detail="User has no preferred channel configured")
    # Create session_question
    session_question = models.SessionQuestion(
        session_id=session_obj.id,
        question_id=question_obj.id,
        channel_id=user_channel.channel_id,
        sent_at=datetime.utcnow(),
        status="pending"
    )
    db_session.add(session_question)
    db_session.commit()

    # Prepare payload for external service
    payload = {
        "session_id": str(session_obj.id),
        "session_question_id": session_question.id,
        "external_session_id": handoff_in.external_session_id,
        "question_text": handoff_in.question_text,
        "answer_type": handoff_in.answer_type,
        "possible_answers": handoff_in.possible_answers,
        "channel_type": user_channel.channel.type,
        "channel_config": user_channel.channel.config,
        "user_contact_details": user_channel.contact_details,
        "user_id": user.id,
        "channel_id": user_channel.channel_id
    }
    # Call the external service
    try:
        resp = requests.post(
            "https://n8n.codeshare.live/webhook/slack-handoff",
            json=payload,
            timeout=10
        )
        resp.raise_for_status()
    except Exception as e:
        # Optionally log or handle the error
        pass

    return {
        "session_id": str(session_obj.id),
        "session_question_id": session_question.id,
        "user_id": user.id,
        "channel_id": user_channel.channel_id
    }
