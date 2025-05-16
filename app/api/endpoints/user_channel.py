from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, schemas, db

router = APIRouter()

CHANNEL_USER_IDENTIFIER = {
    "whatsapp": "phone",
    "telegram": "phone",
    "email": "email",
    "gmail": "email",
    "microsoft outlook": "email",
    "microsoft teams": "email",
    "google chat": "email",
    "slack": "email",
    "discord": "email"
}

@router.post("/", response_model=schemas.UserChannelOut)
def create_user_channel(user_channel_in: schemas.UserChannelCreate, db_session: DBSession = Depends(db.get_db)):
    print(f"create_user_channel: {user_channel_in}")
    # Check if user exists
    # Check if already exists
    existing = db_session.query(models.UserChannel).filter_by(
        user_id=user_channel_in.user_id,
        channel_id=user_channel_in.channel_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already linked to this channel")
    # Validate user identifier for the channel from contact_details
    channel = db_session.query(models.Channel).filter_by(id=user_channel_in.channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    identifier_field = CHANNEL_USER_IDENTIFIER.get(channel.type.lower())
    print(f"identifier_field: {identifier_field}")
    if identifier_field:
        contact_value = user_channel_in.contact_details.get(identifier_field)
        if not contact_value:
            raise HTTPException(status_code=400, detail=f"contact_details must include '{identifier_field}' for channel type '{channel.type}'")
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

@router.get("/", response_model=list[schemas.UserChannelOut])
def list_user_channels(db_session: DBSession = Depends(db.get_db)):
    return db_session.query(models.UserChannel).all()

@router.get("/{user_channel_id}", response_model=schemas.UserChannelOut)
def get_user_channel(user_channel_id: int, db_session: DBSession = Depends(db.get_db)):
    uc = db_session.query(models.UserChannel).filter_by(id=user_channel_id).first()
    if not uc:
        raise HTTPException(status_code=404, detail="User-Channel mapping not found")
    return uc

@router.put("/{user_channel_id}", response_model=schemas.UserChannelOut)
def update_user_channel(user_channel_id: int, user_channel_in: schemas.UserChannelCreate, db_session: DBSession = Depends(db.get_db)):
    uc = db_session.query(models.UserChannel).filter_by(id=user_channel_id).first()
    if not uc:
        raise HTTPException(status_code=404, detail="User-Channel mapping not found")
    uc.user_id = user_channel_in.user_id
    uc.channel_id = user_channel_in.channel_id
    uc.contact_details = user_channel_in.contact_details
    uc.is_preferred = user_channel_in.is_preferred or False
    db_session.commit()
    db_session.refresh(uc)
    return uc

@router.delete("/{user_channel_id}")
def delete_user_channel(user_channel_id: int, db_session: DBSession = Depends(db.get_db)):
    uc = db_session.query(models.UserChannel).filter_by(id=user_channel_id).first()
    if not uc:
        raise HTTPException(status_code=404, detail="User-Channel mapping not found")
    db_session.delete(uc)
    db_session.commit()
    return {"status": "deleted"}
