from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.auth import RequireSecurityScanner
from dependencies.database import get_db
from models.auth import User
from schemas.security import SecurityDashboardResponse, SecurityScanRequest, SecurityScanResponse
from services.checkin_service import CheckInService

router = APIRouter(prefix='/security', tags=['security'])
require_security_scanner = RequireSecurityScanner()


@router.get('/dashboard', response_model=SecurityDashboardResponse)
async def security_dashboard(
    _scanner: User = Depends(require_security_scanner),
    db: AsyncSession = Depends(get_db),
):
    return await CheckInService(db).dashboard_statistics()


@router.post('/scan', response_model=SecurityScanResponse)
async def scan_pass(
    payload: SecurityScanRequest,
    _scanner: User = Depends(require_security_scanner),
    db: AsyncSession = Depends(get_db),
):
    result = await CheckInService(db).preview_scan(payload.qr_token)
    return SecurityScanResponse(**result)


@router.post('/check-in', response_model=SecurityScanResponse)
async def check_in_pass(
    payload: SecurityScanRequest,
    scanner: User = Depends(require_security_scanner),
    db: AsyncSession = Depends(get_db),
):
    result = await CheckInService(db).confirm_scan(payload.qr_token, scanner_id=scanner.id)
    return SecurityScanResponse(**result)
