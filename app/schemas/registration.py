
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class RegistrationCreate(BaseModel):
    full_name: str = Field(..., example="Akshaj Pydimarri", min_length=1, max_length=200)
    email: EmailStr = Field(..., example="akshaj@example.com")
    phone: str = Field(..., example="+919123456789", min_length=10, max_length=20)
    date_of_birth: date = Field(..., example="2000-01-01")
    address: Optional[str] = Field(None, example="Hyderabad, India", max_length=500)

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Full name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', v)
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValueError('Phone number must be 10-15 digits, optionally starting with +')
        return cleaned

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        if isinstance(v, str):
            try:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Date of birth must be in YYYY-MM-DD format (e.g., 1990-01-01)')

        today = date.today()
        if v >= today:
            raise ValueError('Date of birth must be in the past')

        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age > 150:
            raise ValueError('Date of birth seems unrealistic (age > 150 years)')

        return v


class RegistrationUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', v)
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValueError('Phone number must be 10-15 digits, optionally starting with +')
        return cleaned


class RegistrationOut(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
