from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import models, schemas, db

router = APIRouter()

@router.post("/", response_model=schemas.UserOut)
def create_user(user_in: schemas.UserCreate, db_session: DBSession = Depends(db.get_db)):
    # Check if email already exists (optional)
    if user_in.email:
        existing = db_session.query(models.User).filter_by(email=user_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    user_obj = models.User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        persona=user_in.persona
    )
    db_session.add(user_obj)
    db_session.commit()
    db_session.refresh(user_obj)
    return user_obj
