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
    func,
)
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class EventStatus:
    Draft = 'draft'
    Published = 'published'
    RegistrationOpen = 'registration_open'
    RegistrationClosed = 'registration_closed'
    Ongoing = 'ongoing'
    Completed = 'completed'
    Cancelled = 'cancelled'


class EventVisibility:
    Public = 'public'
    Private = 'private'
    DepartmentOnly = 'department_only'


class Event(Base):
    __tablename__ = 'events'

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    title: str = Column(String(300), nullable=False)
    slug: str = Column(String(300), nullable=False, unique=True)
    description: Optional[str] = Column(Text, nullable=True)
    banner_image: Optional[str] = Column(String(1024), nullable=True)

    start_datetime: Optional[datetime] = Column(DateTime(timezone=True), nullable=False)
    end_datetime: Optional[datetime] = Column(DateTime(timezone=True), nullable=False)
    registration_start: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    registration_end: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    venue_id: Optional[str] = Column(String(36), ForeignKey('venues.id', ondelete='SET NULL'), nullable=True)
    department_id: Optional[str] = Column(String(36), ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    academic_year_id: Optional[str] = Column(String(36), ForeignKey('academic_years.id', ondelete='SET NULL'), nullable=True)

    capacity: Optional[int] = Column(Integer, nullable=True)
    registered_count: int = Column(Integer, nullable=False, default=0)

    status: str = Column(String(50), nullable=False, server_default=EventStatus.Draft)
    visibility: str = Column(String(50), nullable=False, server_default=EventVisibility.Public)

    allow_waitlist: bool = Column(Boolean, nullable=False, default=False)
    requires_approval: bool = Column(Boolean, nullable=False, default=False)
    requires_payment: bool = Column(Boolean, nullable=False, default=False)
    price: Optional[float] = Column(Float, nullable=True)

    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    deleted_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # relationships (optional)
    venue = relationship('Venue')
    department = relationship('Department')
    academic_year = relationship('AcademicYear')

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','published','registration_open','registration_closed','ongoing','completed','cancelled')",
            name='ck_events_status',
        ),
        CheckConstraint(
            "visibility IN ('public','private','department_only')",
            name='ck_events_visibility',
        ),
        Index('ix_events_slug', 'slug'),
        Index('ix_events_start', 'start_datetime'),
        Index('ix_events_status', 'status'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Event id={self.id} title={self.title!r} start={self.start_datetime}>"
