import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class RegistrationBase(BaseModel):
    event_id: Optional[str] = None
    user_id: Optional[int] = None
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


class RegistrationCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    academic_year: str = Field(..., min_length=1)
    roll_number: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=7)
    email: str
    gender: str = Field(..., min_length=1)
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_proof: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.replace(' ', '').replace('-', '')
        if not cleaned.isdigit() or len(cleaned) < 7:
            raise ValueError('Phone number must contain at least 7 digits')
        return value

    @field_validator('roll_number')
    @classmethod
    def validate_roll_number(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Roll number is required')
        return value.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', normalized):
            raise ValueError('Please enter a valid email address')
        return normalized

    @field_validator('payment_mode')
    @classmethod
    def validate_payment_mode(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in {'upi', 'cash'}:
            raise ValueError('Payment mode must be either "upi" or "cash"')
        return normalized

    @field_validator('payment_reference')
    @classmethod
    def validate_payment_reference(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) > 255:
            raise ValueError('Payment reference must not exceed 255 characters')
        return value.strip() if value else None

    @field_validator('payment_proof')
    @classmethod
    def validate_payment_proof(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) > 1024:
            raise ValueError('Payment proof path/URI must not exceed 1024 characters')
        return value.strip() if value else None


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


class RegistrationSubmissionResponse(BaseModel):
    registration_number: str
    status: str
    email: str
    message: str
    confirmation_email_sent: bool = True


class PublicRegistrationStatusRequest(BaseModel):
    email: str


class PublicRegistrationStatusResponse(BaseModel):
    found: bool
    status: Optional[str] = None
    registration_number: Optional[str] = None
    message: str
    email_action_available: bool = False


class PublicEmailActionResponse(BaseModel):
    email_sent: bool
    message: str
