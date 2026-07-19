from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EntryLogBase(BaseModel):
    event_id: str
    pass_id: Optional[str] = None
    qr_code_id: Optional[str] = None
    gate_id: Optional[str] = None
    scanned_by: Optional[int] = None
    entry_status: str
    failure_reason: Optional[str] = None
    device_identifier: Optional[str] = None
    scan_timestamp: Optional[datetime] = None


class EntryLogCreate(EntryLogBase):
    pass


class EntryLogUpdate(BaseModel):
    entry_status: Optional[str] = None
    failure_reason: Optional[str] = None
    device_identifier: Optional[str] = None
    scan_timestamp: Optional[datetime] = None


class EntryLogResponse(EntryLogBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
