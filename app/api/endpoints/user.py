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

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db_session: DBSession = Depends(db.get_db)):
    return db_session.query(models.User).all()

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db_session: DBSession = Depends(db.get_db)):
    user = db_session.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_in: schemas.UserCreate, db_session: DBSession = Depends(db.get_db)):
    user = db_session.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user_in.name
    user.email = user_in.email
    user.phone = user_in.phone
    user.persona = user_in.persona
    db_session.commit()
    db_session.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db_session: DBSession = Depends(db.get_db)):
    user = db_session.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_session.delete(user)
    db_session.commit()
    return {"status": "deleted"}
