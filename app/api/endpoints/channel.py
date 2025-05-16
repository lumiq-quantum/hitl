from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, schemas, db
from typing import Dict

router = APIRouter()

ALLOWED_CHANNELS = {
    "discord": ["bot_token", "guild_id"],
    "gmail": ["client_id", "client_secret", "refresh_token"],
    "google chat": ["service_account_json", "space_id"],
    "microsoft outlook": ["client_id", "client_secret", "tenant_id", "refresh_token"],
    "microsoft teams": ["client_id", "client_secret", "tenant_id", "bot_id", "bot_password"],
    "email": ["smtp_server", "smtp_port", "smtp_user", "smtp_password"],
    "slack": ["bot_token", "channel_id"],
    "telegram": ["bot_token", "chat_id"],
    "whatsapp": ["api_key", "phone_number_id"]
}

@router.post("/", response_model=schemas.ChannelOut)
def create_channel(channel_in: schemas.ChannelCreate, db_session: DBSession = Depends(db.get_db)):
    channel_type = channel_in.type.lower()
    if channel_type not in ALLOWED_CHANNELS:
        raise HTTPException(status_code=400, detail=f"Channel type '{channel_in.type}' is not allowed.")
    required_fields = ALLOWED_CHANNELS[channel_type]
    config = channel_in.config or {}
    missing = [field for field in required_fields if field not in config or not config[field]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required config fields for {channel_in.type}: {', '.join(missing)}")
    existing = db_session.query(models.Channel).filter_by(name=channel_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel with this name already exists")
    channel_obj = models.Channel(
        name=channel_in.name,
        type=channel_type,
        config=config
    )
    db_session.add(channel_obj)
    db_session.commit()
    db_session.refresh(channel_obj)
    return channel_obj

@router.get("/", response_model=list[schemas.ChannelOut])
def list_channels(db_session: DBSession = Depends(db.get_db)):
    return db_session.query(models.Channel).all()

@router.get("/{channel_id}", response_model=schemas.ChannelOut)
def get_channel(channel_id: int, db_session: DBSession = Depends(db.get_db)):
    channel = db_session.query(models.Channel).filter_by(id=channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@router.put("/{channel_id}", response_model=schemas.ChannelOut)
def update_channel(channel_id: int, channel_in: schemas.ChannelCreate, db_session: DBSession = Depends(db.get_db)):
    channel = db_session.query(models.Channel).filter_by(id=channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel.name = channel_in.name
    channel.type = channel_in.type
    channel.config = channel_in.config
    db_session.commit()
    db_session.refresh(channel)
    return channel

@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db_session: DBSession = Depends(db.get_db)):
    # Delete related session_questions
    db_session.query(models.SessionQuestion).filter_by(channel_id=channel_id).delete()
    # Delete the channel
    channel = db_session.query(models.Channel).filter_by(id=channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    db_session.delete(channel)
    db_session.commit()
    return {"status": "deleted"}
