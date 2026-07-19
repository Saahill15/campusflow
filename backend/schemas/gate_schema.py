from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class GateBase(BaseModel):
    event_id: str
    name: str
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class GateCreate(GateBase):
    pass


class GateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class GateResponse(GateBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
