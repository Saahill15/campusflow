from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.common import PaginationMeta


class AdminRegistrationItem(BaseModel):
    id: str
    registration_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    academic_year: Optional[str] = None
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    status: str
    created_at: datetime
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminRegistrationDetail(AdminRegistrationItem):
    user_id: Optional[int] = None
    payment_status: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_amount: Optional[float] = None
    payment_reference: Optional[str] = None
    payment_proof: Optional[str] = None
    checked_in: Optional[bool] = None
    checked_in_at: Optional[datetime] = None
    notes: Optional[str] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class AdminRegistrationListResponse(BaseModel):
    items: list[AdminRegistrationItem]
    meta: PaginationMeta


class AdminRegistrationRejectionRequest(BaseModel):
    reason: str


class AdminRegistrationApprovalResponse(BaseModel):
    registration_number: str
    status: str
    approved_at: datetime
    notification_email_sent: bool = True
    message: str | None = None


class AdminRegistrationRejectionResponse(BaseModel):
    registration_number: str
    status: str
    rejected_reason: str
    notification_email_sent: bool = True
    message: str | None = None


class AdminPassQRCode(BaseModel):
    qr_token: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminPassResponse(BaseModel):
    id: str
    pass_number: Optional[str] = None
    status: Optional[str] = None
    issued_at: Optional[datetime] = None
    qr: Optional[AdminPassQRCode] = None

    model_config = {"from_attributes": True}

