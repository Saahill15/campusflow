from pydantic import BaseModel
from typing import Optional


class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[dict] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: bool
