import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    Float,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class RegistrationStatus:
    Pending = 'pending'
    Approved = 'approved'
    Rejected = 'rejected'
    Cancelled = 'cancelled'
    CheckedIn = 'checked_in'


class PaymentStatus:
    NotRequired = 'not_required'
    Pending = 'pending'
    Verified = 'verified'
    Rejected = 'rejected'


class Registration(Base):
    __tablename__ = 'registrations'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)

    event_id: str = Column(String(36), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id: Optional[int] = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)

    first_name: Optional[str] = Column(String(150), nullable=True)
    last_name: Optional[str] = Column(String(150), nullable=True)
    department: Optional[str] = Column(String(150), nullable=True)
    academic_year: Optional[str] = Column(String(100), nullable=True)
    roll_number: Optional[str] = Column(String(100), nullable=True)
    phone: Optional[str] = Column(String(50), nullable=True)
    email: Optional[str] = Column(String(255), nullable=True)
    gender: Optional[str] = Column(String(50), nullable=True)

    registration_number: Optional[str] = Column(String(100), unique=True, nullable=True)

    status: str = Column(String(50), nullable=False, server_default=RegistrationStatus.Pending)

    payment_status: str = Column(String(50), nullable=False, server_default=PaymentStatus.NotRequired)
    payment_mode: Optional[str] = Column(String(100), nullable=True)
    payment_amount: Optional[float] = Column(Float, nullable=True)
    payment_reference: Optional[str] = Column(String(255), nullable=True)
    payment_proof: Optional[str] = Column(String(1024), nullable=True)

    approved_by: Optional[int] = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approved_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    rejected_reason: Optional[str] = Column(Text, nullable=True)

    checked_in: bool = Column(Boolean, nullable=False, default=False)
    checked_in_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    notes: Optional[str] = Column(Text, nullable=True)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    deleted_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # relationships
    event = relationship('Event')
    user = relationship('User', foreign_keys=[user_id])
    approved_by_user = relationship('User', foreign_keys=[approved_by])

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected','cancelled','checked_in')",
            name='ck_registrations_status',
        ),
        CheckConstraint(
            "payment_status IN ('not_required','pending','verified','rejected')",
            name='ck_registrations_payment_status',
        ),
        UniqueConstraint('event_id', 'user_id', name='uq_registration_event_user'),
        Index('ix_registrations_event_id', 'event_id'),
        Index('ix_registrations_registration_number', 'registration_number'),
        Index('ix_registrations_status', 'status'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Registration id={self.id} event={self.event_id} user={self.user_id} status={self.status}>"
