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
    Index,
    func,
)
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Gate(Base):
    __tablename__ = 'gates'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)

    event_id: str = Column(String(36), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)

    name: str = Column(String(200), nullable=False)
    description: Optional[str] = Column(String(1024), nullable=True)
    display_order: Optional[int] = Column(Integer, nullable=True)

    is_active: bool = Column(Boolean, nullable=False, default=True)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    deleted_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # relationship
    event = relationship('Event')

    __table_args__ = (
        Index('ix_gates_event_id', 'event_id'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Gate id={self.id} name={self.name} event={self.event_id}>"
