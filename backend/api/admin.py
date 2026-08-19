from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from dependencies.auth import RequireRole
from dependencies.database import get_db
from models.auth import Role, User, users_roles
from models.registration import Registration
from schemas.admin import (
    AdminPassQRCode,
    AdminPassResponse,
    AdminDashboardResponse,
    AdminRegistrationApprovalResponse,
    AdminRegistrationDetail,
    AdminRegistrationListResponse,
    AdminRegistrationRejectionRequest,
    AdminRegistrationRejectionResponse,
    AdminRegistrationUpdate,
    AdminEmailActionResponse,
    AdminRollNumberFixResponse,
)
from schemas.common import PaginationMeta
from schemas.system_settings import SystemSettingsResponse, SystemSettingsUpdate
from services.admin_registration_service import AdminRegistrationService
from services.system_settings_service import SystemSettingsService
from services.email_service import (
    build_registration_rejection_email,
    get_email_service,
)
from services.registration_email_service import (
    build_existing_pass_attachment,
    send_confirmation_email,
    send_existing_pass_email,
)
from services.pass_service import PassService
from services.qr_service import QRCodeService
from services.registration_service import RegistrationService
from services.auth_service import hash_password
from schemas.security import SecurityVolunteerCreate, SecurityVolunteerResponse, SecurityVolunteerStatusUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/admin', tags=['admin'])
require_admin = RequireRole('admin')


@router.get('/security-volunteers', response_model=list[SecurityVolunteerResponse])
async def list_security_volunteers(
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).join(User.roles).where(Role.name == 'security_volunteer').options(selectinload(User.roles)).order_by(User.created_at.desc())
    )
    return result.scalars().unique().all()


@router.post('/security-volunteers', response_model=SecurityVolunteerResponse, status_code=status.HTTP_201_CREATED)
async def create_security_volunteer(
    payload: SecurityVolunteerCreate,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='A user with this email already exists.')
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Passwords do not match.')

    role = (await db.execute(select(Role).where(Role.name == 'security_volunteer'))).scalars().first()
    if not role:
        role = Role(name='security_volunteer', description='On-day QR scanning and check-in role')
        db.add(role)
        await db.flush()
    user = User(email=payload.email, hashed_password=hash_password(payload.password), is_active=True, is_verified=True)
    user.roles = [role]
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch('/security-volunteers/{user_id}', response_model=SecurityVolunteerResponse)
async def update_security_volunteer(
    user_id: int,
    payload: SecurityVolunteerStatusUpdate,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id).options(selectinload(User.roles)))
    user = result.scalars().first()
    if not user or not any(role.name == 'security_volunteer' for role in user.roles):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Security volunteer not found')
    user.is_active = payload.is_active
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _get_pass_artifact(registration_id: str, db: AsyncSession):
    registration = (await db.execute(select(Registration).where(Registration.id == registration_id))).scalars().first()
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registration not found')

    pass_obj = await PassService(db).get_by_registration(registration_id)
    if not pass_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pass not found')

    attachments = await build_existing_pass_attachment(db, registration, pass_obj)
    return registration, pass_obj, attachments[0][1]


@router.get('/dashboard/summary', response_model=AdminDashboardResponse)
async def get_dashboard_summary(
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminRegistrationService(db)
    return await service.get_dashboard_summary()


@router.get('/settings', response_model=SystemSettingsResponse)
async def get_system_settings(
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    settings = await SystemSettingsService(db).get_settings()
    return SystemSettingsResponse.model_validate(settings)


@router.patch('/settings', response_model=SystemSettingsResponse)
async def update_system_settings(
    payload: SystemSettingsUpdate,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    settings = await SystemSettingsService(db).update_settings(changes)
    return SystemSettingsResponse.model_validate(settings)


@router.get('/registrations', response_model=AdminRegistrationListResponse)
async def list_registrations(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: str = Query('all', alias='status'),
    search: str | None = Query(None),
    payment_status: str | None = Query(None),
    department: str | None = Query(None),
    academic_year: str | None = Query(None),
    checked_in: bool | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminRegistrationService(db)
    items, total, filters = await service.list_registrations(
        page=page,
        per_page=per_page,
        status=status_filter,
        search=search,
        payment_status=payment_status,
        department=department,
        academic_year=academic_year,
        checked_in=checked_in,
        date_from=date_from,
        date_to=date_to,
    )
    return AdminRegistrationListResponse(
        items=items,
        meta=PaginationMeta(total=total, page=page, per_page=per_page),
        filters=filters,
    )


@router.get('/registrations/{registration_id}', response_model=AdminRegistrationDetail)
async def get_registration(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminRegistrationService(db)
    registration = await service.get_registration(registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registration not found')
    return registration


@router.patch('/registrations/{registration_id}', response_model=AdminRegistrationDetail)
async def update_registration(
    registration_id: str,
    payload: AdminRegistrationUpdate,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminRegistrationService(db)
    try:
        return await service.update_registration(
            registration_id,
            payload.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        if str(exc) == 'Registration not found':
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.patch('/registrations/{registration_id}/fix-roll-number', response_model=AdminRollNumberFixResponse)
async def fix_roll_number(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        registration, previous, corrected, changed = await AdminRegistrationService(db).fix_roll_number(registration_id)
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if str(exc) == 'Registration not found' else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    return AdminRollNumberFixResponse(
        registration_number=registration.registration_number,
        previous_roll_number=previous,
        roll_number=corrected,
        changed=changed,
        message='Roll number corrected successfully.' if changed else 'Roll number is already in the correct format.',
    )


@router.post('/registrations/{registration_id}/approve', response_model=AdminRegistrationApprovalResponse)
async def approve_registration(
    registration_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    service = RegistrationService(db)
    try:
        registration = await service.approve_registration(registration_id, _admin.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    pass_service = PassService(db)
    p = await pass_service.get_by_registration(registration.id)

    notification_email_sent = False
    message = None
    if p:
        notification_email_sent, message = await send_existing_pass_email(db, registration, p, email_service)
    else:
        message = 'Registration approved, but pass could not be found.'

    response = AdminRegistrationApprovalResponse(
        registration_number=registration.registration_number,
        status=registration.status,
        approved_at=registration.approved_at,
        notification_email_sent=notification_email_sent,
        message=message,
    )
    return response


@router.post('/registrations/{registration_id}/reject', response_model=AdminRegistrationRejectionResponse)
async def reject_registration(
    registration_id: str,
    payload: AdminRegistrationRejectionRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    service = RegistrationService(db)
    try:
        registration = await service.reject_registration(registration_id, _admin.id, payload.reason)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    email_enabled = getattr(email_service, 'enabled', False)
    notification_email_sent = False
    message = 'Email notifications are disabled.' if not email_enabled else None

    if registration.email and email_enabled and (await SystemSettingsService(db).get_settings()).email_enabled:
        subject, body = build_registration_rejection_email(registration.registration_number, payload.reason)
        try:
            await email_service.send_email(registration.email, subject, body)
            notification_email_sent = True
        except Exception:
            notification_email_sent = False
            message = 'Registration rejected, but notification email could not be delivered.'
            logger.exception('Registration rejection email delivery failed for %s', registration.email)
    elif registration.email and email_enabled:
        message = 'Email sending is currently disabled.'

    response = AdminRegistrationRejectionResponse(
        registration_number=registration.registration_number,
        status=registration.status,
        rejected_reason=registration.rejected_reason,
        notification_email_sent=notification_email_sent,
        message=message,
    )
    return response



@router.get('/registrations/{registration_id}/pass', response_model=AdminPassResponse)
async def get_registration_pass(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    pass_service = PassService(db)
    qr_service = QRCodeService(db)

    p = await pass_service.get_by_registration(registration_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pass not found')

    q = await qr_service.get_by_pass(p.id)
    qr_obj = None
    if q:
        qr_obj = AdminPassQRCode(qr_token=q.qr_token)

    return AdminPassResponse(
        id=p.id,
        pass_number=p.pass_number,
        status=p.status,
        issued_at=p.issued_at,
        qr=qr_obj,
    )


@router.get('/registrations/{registration_id}/pass/download')
async def download_registration_pass(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    _registration, _pass_obj, png_bytes = await _get_pass_artifact(registration_id, db)
    return Response(
        content=png_bytes,
        media_type='image/png',
        headers={'Content-Disposition': 'attachment; filename="Pragyarambh_Pass.png"'},
    )


@router.post('/registrations/{registration_id}/resend-confirmation-email', response_model=AdminEmailActionResponse)
async def resend_confirmation_email(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    registration = await AdminRegistrationService(db).get_registration(registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registration not found')
    if registration.status == 'approved':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Approved registrations must receive the existing pass email.')
    sent, message = await send_confirmation_email(registration, email_service, db)
    return AdminEmailActionResponse(
        registration_number=registration.registration_number,
        email_sent=sent,
        message=message or 'Confirmation email sent successfully.',
    )


@router.post('/registrations/{registration_id}/send-pass-email', response_model=AdminEmailActionResponse)
async def send_pass_email(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    registration = await AdminRegistrationService(db).get_registration(registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registration not found')
    if registration.status != 'approved':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only approved registrations can receive a pass email.')
    pass_obj = await PassService(db).get_by_registration(registration_id)
    if not pass_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pass not found')
    sent, message = await send_existing_pass_email(db, registration, pass_obj, email_service)
    return AdminEmailActionResponse(
        registration_number=registration.registration_number,
        pass_number=pass_obj.pass_number,
        email_sent=sent,
        message=message or 'Pass email sent successfully.',
    )


@router.post('/registrations/{registration_id}/resend-approval-email')
async def resend_approval_email(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    registration = await AdminRegistrationService(db).get_registration(registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registration not found')
    pass_obj = await PassService(db).get_by_registration(registration_id)
    if not pass_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pass not found')
    if registration.status != 'approved':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only approved registrations can receive an approval email')
    sent, message = await send_existing_pass_email(db, registration, pass_obj, email_service)
    return {
        'registration_number': registration.registration_number,
        'pass_number': pass_obj.pass_number,
        'email_sent': sent,
        'message': message,
    }
