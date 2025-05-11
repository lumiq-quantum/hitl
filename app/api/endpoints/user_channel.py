from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, schemas, db

router = APIRouter()

@router.post("/", response_model=schemas.UserChannelOut)
def create_user_channel(user_channel_in: schemas.UserChannelCreate, db_session: DBSession = Depends(db.get_db)):
    # Check if already exists
    existing = db_session.query(models.UserChannel).filter_by(
        user_id=user_channel_in.user_id,
        channel_id=user_channel_in.channel_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already linked to this channel")
    user_channel_obj = models.UserChannel(
        user_id=user_channel_in.user_id,
        channel_id=user_channel_in.channel_id,
        contact_details=user_channel_in.contact_details,
        is_preferred=user_channel_in.is_preferred or False
    )
    db_session.add(user_channel_obj)
    db_session.commit()
    db_session.refresh(user_channel_obj)
    return user_channel_obj
