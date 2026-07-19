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
    CheckConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class QRStatus:
    Pending = 'pending'
    Active = 'active'
    Revoked = 'revoked'
    Expired = 'expired'


class QRCode(Base):
    __tablename__ = 'qrcodes'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)

    pass_id: str = Column(String(36), ForeignKey('passes.id', ondelete='CASCADE'), nullable=False, unique=True)

    qr_token: Optional[str] = Column(String(255), nullable=True, unique=True)
    status: str = Column(String(50), nullable=False, server_default=QRStatus.Pending)

    generated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    activated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    revoked_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    last_scanned_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    scan_count: int = Column(Integer, nullable=False, default=0)

    is_active: bool = Column(Boolean, nullable=False, default=True)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    deleted_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # relationships
    pass_obj = relationship('Pass')

    __table_args__ = (
        CheckConstraint("status IN ('pending','active','revoked','expired')", name='ck_qrcodes_status'),
        Index('ix_qrcodes_qr_token', 'qr_token'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<QRCode id={self.id} pass_id={self.pass_id} token={self.qr_token}>"
