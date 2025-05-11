from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, schemas, db

router = APIRouter()

@router.post("/", response_model=schemas.ChannelOut)
def create_channel(channel_in: schemas.ChannelCreate, db_session: DBSession = Depends(db.get_db)):
    existing = db_session.query(models.Channel).filter_by(name=channel_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel with this name already exists")
    channel_obj = models.Channel(
        name=channel_in.name,
        type=channel_in.type,
        config=channel_in.config
    )
    db_session.add(channel_obj)
    db_session.commit()
    db_session.refresh(channel_obj)
    return channel_obj
