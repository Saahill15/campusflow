from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RegistrationBase(BaseModel):
    event_id: str
    user_id: int
    registration_number: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_amount: Optional[float] = None
    payment_reference: Optional[str] = None
    payment_proof: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    checked_in: Optional[bool] = None
    checked_in_at: Optional[datetime] = None
    notes: Optional[str] = None


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationUpdate(BaseModel):
    registration_number: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_amount: Optional[float] = None
    payment_reference: Optional[str] = None
    payment_proof: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    checked_in: Optional[bool] = None
    checked_in_at: Optional[datetime] = None
    notes: Optional[str] = None


class RegistrationResponse(RegistrationBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
