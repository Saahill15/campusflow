from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr, Field, ConfigDict


class SecurityScanRequest(BaseModel):
    qr_token: str
    gate_id: str


class SecurityScanResponse(BaseModel):
    status: str
    message: str
    student_name: Optional[str] = None
    registration_number: Optional[str] = None
    pass_number: Optional[str] = None
    department: Optional[str] = None
    academic_year: Optional[str] = None
    event: Optional[str] = None
    checked_in: bool = False
    checked_in_at: Optional[datetime] = None
    entry_log_id: Optional[str] = None


class SecurityGateResponse(BaseModel):
    id: str
    name: str


class SecurityVolunteerResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SecurityVolunteerCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class SecurityVolunteerStatusUpdate(BaseModel):
    is_active: bool
