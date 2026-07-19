import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class EntryStatus:
    Success = 'success'
    Duplicate = 'duplicate'
    Revoked = 'revoked'
    Expired = 'expired'
    Invalid = 'invalid'
    Rejected = 'rejected'


class EntryLog(Base):
    __tablename__ = 'entry_logs'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)

    event_id: str = Column(String(36), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    pass_id: Optional[str] = Column(String(36), ForeignKey('passes.id', ondelete='SET NULL'), nullable=True)
    qr_code_id: Optional[str] = Column(String(36), ForeignKey('qrcodes.id', ondelete='SET NULL'), nullable=True)
    gate_id: Optional[str] = Column(String(36), ForeignKey('gates.id', ondelete='SET NULL'), nullable=True)

    scanned_by: Optional[int] = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    entry_status: str = Column(String(50), nullable=False)
    failure_reason: Optional[str] = Column(Text, nullable=True)
    device_identifier: Optional[str] = Column(String(255), nullable=True)

    scan_timestamp: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    # relationships
    event = relationship('Event')
    pass_obj = relationship('Pass')
    qr_code = relationship('QRCode')
    gate = relationship('Gate')
    scanner = relationship('User')

    __table_args__ = (
        CheckConstraint("entry_status IN ('success','duplicate','revoked','expired','invalid','rejected')", name='ck_entry_logs_status'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<EntryLog id={self.id} status={self.entry_status} event={self.event_id}>"
