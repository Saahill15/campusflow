from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PassBase(BaseModel):
    event_id: str
    registration_id: str
    pass_number: Optional[str] = None
    pass_type: Optional[str] = None
    status: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class PassCreate(PassBase):
    pass


class PassUpdate(BaseModel):
    pass_number: Optional[str] = None
    pass_type: Optional[str] = None
    status: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class PassResponse(PassBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
