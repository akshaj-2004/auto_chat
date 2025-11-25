
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.registration import RegistrationCreate, RegistrationUpdate, RegistrationOut
from app.services.reg_service import (
    create_registration,
    get_registration,
    list_registrations,
    update_registration,
    delete_registration,
    get_registration_by_email
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=RegistrationOut)
def create_user(payload: RegistrationCreate, db: Session = Depends(get_db)):
    if get_registration_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_registration(db, payload)
    return new_user


@router.get("/", response_model=list[RegistrationOut])
def list_users(db: Session = Depends(get_db)):
    users = list_registrations(db)
    return users


@router.get("/{user_id}", response_model=RegistrationOut)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = get_registration(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=RegistrationOut)
def update_user(user_id: UUID, payload: RegistrationUpdate, db: Session = Depends(get_db)):
    user = get_registration(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = update_registration(db, user, payload)
    return updated


@router.delete("/{user_id}")
def delete_user_route(user_id: UUID, db: Session = Depends(get_db)):
    user = get_registration(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_registration(db, user)
    return {"detail": "User deleted successfully"}
