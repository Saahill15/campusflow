from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.auth import RequireSecurityScanner
from dependencies.database import get_db
from models.auth import User
from models.gate import Gate
from schemas.security import SecurityDashboardResponse, SecurityGateResponse, SecurityScanRequest, SecurityScanResponse
from services.checkin_service import CheckInService

router = APIRouter(prefix='/security', tags=['security'])
require_security_scanner = RequireSecurityScanner()


@router.get('/gates', response_model=list[SecurityGateResponse])
async def list_security_gates(
    _scanner: User = Depends(require_security_scanner),
    db: AsyncSession = Depends(get_db),
):
    gates = (await db.execute(select(Gate).where(Gate.is_active.is_(True)).order_by(Gate.display_order, Gate.name))).scalars().all()
    return [SecurityGateResponse(id=gate.id, name=gate.name) for gate in gates]


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
    result = await CheckInService(db).preview_scan(payload.qr_token, payload.gate_id)
    return SecurityScanResponse(**result)


@router.post('/check-in', response_model=SecurityScanResponse)
async def check_in_pass(
    payload: SecurityScanRequest,
    scanner: User = Depends(require_security_scanner),
    db: AsyncSession = Depends(get_db),
):
    result = await CheckInService(db).confirm_scan(payload.qr_token, payload.gate_id, scanner_id=scanner.id)
    return SecurityScanResponse(**result)
