from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, db
from datetime import datetime
from pydantic import BaseModel
import requests

router = APIRouter()

class ResponseRequest(BaseModel):
    session_question_id: int
    response: str

@router.post("/")
def submit_response(
    req: ResponseRequest,
    db_session: DBSession = Depends(db.get_db)
):
    session_question = db_session.query(models.SessionQuestion).filter_by(id=req.session_question_id).first()
    if not session_question:
        raise HTTPException(status_code=404, detail="Session question not found")
    if session_question.status == "answered":
        raise HTTPException(status_code=400, detail="Already answered")

    # Fetch session details
    session = session_question.session
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Prepare payload for external API call
    payload = {
        "appName": session.session_info.get("appname"),
        "userId": session.session_info.get("user_id"),
        "sessionId": session.session_info.get("session_id"),
        "newMessage": {
            "role": "user",
            "parts": [
                {"text": req.response}
            ]
        }
    }

    # Make the API call
    try:
        resp = requests.post(
            "http://localhost:8000/run",
            json=payload,
            headers={"accept": "application/json", "Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to notify external system: {str(e)}")

    # Update session question status
    session_question.response = req.response
    session_question.answered_at = datetime.utcnow()
    session_question.status = "answered"
    db_session.commit()

    return {"status": "success", "session_id": str(session_question.session_id)}
