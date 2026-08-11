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


class PassStatus:
    Pending = 'pending'
    Issued = 'issued'
    Revoked = 'revoked'
    Used = 'used'
    Expired = 'expired'


class PassType:
    General = 'general'
    VIP = 'vip'
    Committee = 'committee'
    Organizer = 'organizer'
    Guest = 'guest'


class Pass(Base):
    __tablename__ = 'passes'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)

    event_id: str = Column(String(36), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    registration_id: str = Column(String(36), ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False, unique=True)

    pass_number: Optional[str] = Column(String(100), unique=True, nullable=True)
    pass_type: str = Column(String(50), nullable=False, server_default=PassType.General)
    status: str = Column(String(50), nullable=False, server_default=PassStatus.Pending)

    issued_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    expires_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    checked_in_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    is_active: bool = Column(Boolean, nullable=False, default=True)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    deleted_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # relationships
    event = relationship('Event')
    registration = relationship('Registration')

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','issued','revoked','used','expired')",
            name='ck_passes_status',
        ),
        CheckConstraint(
            "pass_type IN ('general','vip','committee','organizer','guest')",
            name='ck_passes_type',
        ),
        Index('ix_passes_event_id', 'event_id'),
        Index('ix_passes_pass_number', 'pass_number'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Pass id={self.id} registration={self.registration_id} pass_number={self.pass_number}>"
