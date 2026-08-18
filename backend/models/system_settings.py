from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, func

from db.base import Base


class SystemSettings(Base):
    __tablename__ = 'system_settings'

    # A fixed primary key makes this table a true singleton.
    id: int = Column(Integer, primary_key=True, default=1)

    registration_enabled: bool = Column(Boolean, nullable=False, server_default='true', default=True)
    checkin_enabled: bool = Column(Boolean, nullable=False, server_default='true', default=True)
    email_enabled: bool = Column(Boolean, nullable=False, server_default='true', default=True)
    maintenance_mode: bool = Column(Boolean, nullable=False, server_default='false', default=False)

    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime | None = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    __table_args__ = (
        CheckConstraint('id = 1', name='ck_system_settings_singleton_id'),
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<SystemSettings id={self.id}>"
