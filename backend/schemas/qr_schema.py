from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class QRCodeBase(BaseModel):
    pass_id: str
    qr_token: Optional[str] = None
    status: Optional[str] = None
    generated_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    last_scanned_at: Optional[datetime] = None
    scan_count: Optional[int] = None
    is_active: Optional[bool] = None


class QRCodeCreate(QRCodeBase):
    pass


class QRCodeUpdate(BaseModel):
    qr_token: Optional[str] = None
    status: Optional[str] = None
    generated_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    last_scanned_at: Optional[datetime] = None
    scan_count: Optional[int] = None
    is_active: Optional[bool] = None


class QRCodeResponse(QRCodeBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
