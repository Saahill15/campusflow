import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import relationship
from db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Department(Base):
    __tablename__ = 'departments'
    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    name: str = Column(String(200), nullable=False, unique=True)
    description: str = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: datetime = Column(DateTime(timezone=True), nullable=True)

    committees = relationship('Committee', back_populates='department', cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_departments_name', 'name'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Department id={self.id} name={self.name!r}>"


class AcademicYear(Base):
    __tablename__ = 'academic_years'
    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    code: str = Column(String(50), nullable=False, unique=True)
    label: str = Column(String(200), nullable=True)
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: datetime = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_academic_years_code', 'code'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<AcademicYear id={self.id} code={self.code!r}>"


class Committee(Base):
    __tablename__ = 'committees'
    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    department_id: str = Column(String(36), ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    name: str = Column(String(200), nullable=False)
    description: str = Column(Text, nullable=True)
    committee_head_id: str = Column(String(36), nullable=True)  # placeholder for future FK to users
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: datetime = Column(DateTime(timezone=True), nullable=True)

    department = relationship('Department', back_populates='committees')

    __table_args__ = (
        UniqueConstraint('department_id', 'name', name='uq_committee_department_name'),
        Index('ix_committees_department_id', 'department_id'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Committee id={self.id} name={self.name!r} dept={self.department_id}>"


class Venue(Base):
    __tablename__ = 'venues'
    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    name: str = Column(String(200), nullable=False)
    building: str = Column(String(200), nullable=True)
    floor: int = Column(Integer, nullable=True)
    capacity: int = Column(Integer, nullable=True)
    description: str = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: datetime = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_venues_name', 'name'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Venue id={self.id} name={self.name!r} building={self.building!r}>"
