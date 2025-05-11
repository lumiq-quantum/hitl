from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, db
from datetime import datetime
from pydantic import BaseModel

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
    session_question.response = req.response
    session_question.answered_at = datetime.utcnow()
    session_question.status = "answered"
    db_session.commit()
    # Here you would notify the external agent system using session_question.session.external_session_id
    return {"status": "success", "session_id": str(session_question.session_id)}
