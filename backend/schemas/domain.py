from typing import Optional
from pydantic import BaseModel, Field


class _OrmConfig:
    model_config = {"from_attributes": True}


# Department schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: str

    model_config = {"from_attributes": True}


# AcademicYear schemas
class AcademicYearBase(BaseModel):
    code: str
    label: Optional[str] = None
    is_active: Optional[bool] = True


class AcademicYearCreate(AcademicYearBase):
    pass


class AcademicYearUpdate(BaseModel):
    code: Optional[str] = None
    label: Optional[str] = None
    is_active: Optional[bool] = None


class AcademicYearResponse(AcademicYearBase):
    id: str
    model_config = {"from_attributes": True}


# Committee schemas
class CommitteeBase(BaseModel):
    name: str
    description: Optional[str] = None
    committee_head_id: Optional[str] = None
    is_active: Optional[bool] = True


class CommitteeCreate(CommitteeBase):
    department_id: str


class CommitteeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    committee_head_id: Optional[str] = None
    is_active: Optional[bool] = None


class CommitteeResponse(CommitteeBase):
    id: str
    department_id: str
    model_config = {"from_attributes": True}


# Venue schemas
class VenueBase(BaseModel):
    name: str
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class VenueResponse(VenueBase):
    id: str
    model_config = {"from_attributes": True}
