import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    func,
    Index,
)
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class EventSettings(Base):
    __tablename__ = 'event_settings'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)

    event_id: str = Column(String(36), ForeignKey('events.id', ondelete='CASCADE'), nullable=False, unique=True)

    allow_check_in: bool = Column(Boolean, nullable=False, default=True)
    allow_reentry: bool = Column(Boolean, nullable=False, default=False)
    allow_duplicate_scan: bool = Column(Boolean, nullable=False, default=False)
    require_active_qr: bool = Column(Boolean, nullable=False, default=True)
    require_active_pass: bool = Column(Boolean, nullable=False, default=True)
    require_approved_registration: bool = Column(Boolean, nullable=False, default=True)

    checkin_start_time: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    checkin_end_time: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    max_entries_per_person: int = Column(Integer, nullable=False, default=1)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    deleted_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    event = relationship('Event')

    __table_args__ = (
        Index('ix_event_settings_event_id', 'event_id'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<EventSettings id={self.id} event={self.event_id}>"
