from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EventSettingsBase(BaseModel):
    event_id: str
    allow_check_in: Optional[bool] = None
    allow_reentry: Optional[bool] = None
    allow_duplicate_scan: Optional[bool] = None
    require_active_qr: Optional[bool] = None
    require_active_pass: Optional[bool] = None
    require_approved_registration: Optional[bool] = None
    checkin_start_time: Optional[datetime] = None
    checkin_end_time: Optional[datetime] = None
    max_entries_per_person: Optional[int] = None


class EventSettingsCreate(EventSettingsBase):
    pass


class EventSettingsUpdate(BaseModel):
    allow_check_in: Optional[bool] = None
    allow_reentry: Optional[bool] = None
    allow_duplicate_scan: Optional[bool] = None
    require_active_qr: Optional[bool] = None
    require_active_pass: Optional[bool] = None
    require_approved_registration: Optional[bool] = None
    checkin_start_time: Optional[datetime] = None
    checkin_end_time: Optional[datetime] = None
    max_entries_per_person: Optional[int] = None


class EventSettingsResponse(EventSettingsBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
