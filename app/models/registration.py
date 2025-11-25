
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)

    date_of_birth = Column(Date, nullable=False)

    address = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
