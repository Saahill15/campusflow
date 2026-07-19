from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    banner_image: Optional[str] = None
    start_datetime: str
    end_datetime: str
    registration_start: Optional[str] = None
    registration_end: Optional[str] = None
    venue_id: Optional[str] = None
    department_id: Optional[str] = None
    academic_year_id: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = 'draft'
    visibility: Optional[str] = 'public'
    allow_waitlist: Optional[bool] = False
    requires_approval: Optional[bool] = False
    requires_payment: Optional[bool] = False
    price: Optional[float] = None
    is_active: Optional[bool] = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    banner_image: Optional[str] = None
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    registration_start: Optional[str] = None
    registration_end: Optional[str] = None
    venue_id: Optional[str] = None
    department_id: Optional[str] = None
    academic_year_id: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    allow_waitlist: Optional[bool] = None
    requires_approval: Optional[bool] = None
    requires_payment: Optional[bool] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    id: str

    model_config = {"from_attributes": True}
