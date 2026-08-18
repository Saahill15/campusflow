from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SystemSettingsResponse(BaseModel):
    registration_enabled: bool
    checkin_enabled: bool
    email_enabled: bool
    maintenance_mode: bool

    model_config = ConfigDict(from_attributes=True)


class SystemSettingsUpdate(BaseModel):
    registration_enabled: bool | None = None
    checkin_enabled: bool | None = None
    email_enabled: bool | None = None
    maintenance_mode: bool | None = None
