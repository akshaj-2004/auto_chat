
from sqlalchemy.orm import Session
from app.models.registration import Registration
from app.schemas.registration import RegistrationCreate, RegistrationUpdate
import uuid


def create_registration(db: Session, data: RegistrationCreate) -> Registration:
    new_reg = Registration(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        date_of_birth=data.date_of_birth,
        address=data.address,
    )

    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg


def get_registration(db: Session, reg_id: uuid.UUID) -> Registration | None:
    return db.query(Registration).filter(Registration.id == reg_id).first()


def get_registration_by_email(db: Session, email: str) -> Registration | None:
    return db.query(Registration).filter(Registration.email == email).first()


def list_registrations(db: Session, limit: int = 50):
    return (
        db.query(Registration)
        .order_by(Registration.created_at.desc())
        .limit(limit)
        .all()
    )


def update_registration(db: Session, reg: Registration, updates: RegistrationUpdate) -> Registration:
    update_data = updates.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(reg, field, value)

    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def delete_registration(db: Session, reg: Registration):
    db.delete(reg)
    db.commit()
