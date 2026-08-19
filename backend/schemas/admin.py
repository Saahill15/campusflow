from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

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
    payment_status: Optional[str] = None
    pass_number: Optional[str] = None
    pass_status: Optional[str] = None
    checked_in: bool = False
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


class AdminRegistrationUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    academic_year: Optional[str] = None
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class AdminRegistrationFilterOptions(BaseModel):
    departments: list[str] = []
    academic_years: list[str] = []
    payment_statuses: list[str] = []


class AdminRegistrationListResponse(BaseModel):
    items: list[AdminRegistrationItem]
    meta: PaginationMeta
    filters: Optional[AdminRegistrationFilterOptions] = None


class AdminDashboardRecentRegistration(BaseModel):
    registration_number: Optional[str] = None
    student_name: str
    department: Optional[str] = None
    status: str
    created_at: datetime


class AdminDashboardCount(BaseModel):
    label: str
    count: int


class AdminDashboardResponse(BaseModel):
    total_registrations: int
    pending_approval: int
    approved: int
    rejected: int
    checked_in: int
    not_checked_in: int
    recent_registrations: list[AdminDashboardRecentRegistration]
    department_overview: list[AdminDashboardCount]
    academic_year_overview: list[AdminDashboardCount]
    payment_overview: list[AdminDashboardCount]


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

