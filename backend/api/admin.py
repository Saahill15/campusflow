from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from dependencies.auth import RequireRole
from dependencies.database import get_db
from models.auth import User
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
)
from schemas.common import PaginationMeta
from services.admin_registration_service import AdminRegistrationService
from services.email_service import (
    build_registration_approval_email,
    build_registration_rejection_email,
    get_email_service,
)
from services.pass_service import PassService
from services.qr_service import QRCodeService
from services.pdf_service import generate_pass_png_bytes
from services.registration_service import RegistrationService
from models.event import Event

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/admin', tags=['admin'])
require_admin = RequireRole('admin')


async def _get_pass_artifact(registration_id: str, db: AsyncSession):
    registration = (await db.execute(select(Registration).where(Registration.id == registration_id))).scalars().first()
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Registration not found')

    pass_obj = await PassService(db).get_by_registration(registration_id)
    if not pass_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pass not found')

    qr = await QRCodeService(db).get_by_pass(pass_obj.id)
    event_title = (await db.execute(select(Event.title).where(Event.id == registration.event_id))).scalar_one_or_none() or 'Pragyarambh 3.0'
    attendee_name = ' '.join(filter(None, [registration.first_name, registration.last_name])) or 'Attendee'
    png_bytes = generate_pass_png_bytes(
        registration.registration_number or '',
        pass_obj.pass_number or '',
        attendee_name,
        event_title=event_title,
        department=registration.department or '',
        academic_year=registration.academic_year or '',
        qr_token=qr.qr_token if qr else None,
    )
    return registration, pass_obj, png_bytes


async def _send_approval_email(registration, pass_obj, png_bytes, email_service):
    if not registration.email:
        return False, 'Registration has no email address.'
    if not getattr(email_service, 'enabled', False):
        return False, 'Email notifications are disabled.'

    subject, body = build_registration_approval_email(registration.registration_number or '', pass_obj.pass_number or '')
    try:
        await email_service.send_email(
            registration.email,
            subject,
            body,
            attachments=[('Pragyarambh_Pass.png', png_bytes, 'image/png')],
        )
    except Exception:
        logger.exception('Approval email delivery failed for %s', registration.email)
        return False, 'Pass generated, but notification email could not be delivered.'
    return True, None


@router.get('/dashboard/summary', response_model=AdminDashboardResponse)
async def get_dashboard_summary(
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminRegistrationService(db)
    return await service.get_dashboard_summary()


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

    email_enabled = getattr(email_service, 'enabled', False)
    notification_email_sent = False
    message = 'Email notifications are disabled.' if not email_enabled else None

    if registration.email and p and email_enabled:
        subject, body = build_registration_approval_email(registration.registration_number, p.pass_number)
        attachment = None
        try:
            qr = await QRCodeService(db).get_by_pass(p.id)
            qr_token = qr.qr_token if qr else None
            attendee_name = ' '.join(filter(None, [registration.first_name, registration.last_name])) or 'Attendee'
            event_title = 'Pragyarambh 3.0'
            try:
                result = await db.execute(select(Event.title).where(Event.id == registration.event_id))
                event_title = result.scalar_one_or_none() or event_title
            except Exception:
                pass

            png_bytes = generate_pass_png_bytes(
                registration.registration_number,
                p.pass_number,
                attendee_name,
                event_title=event_title,
                department=registration.department or '',
                academic_year=registration.academic_year or '',
                qr_token=qr_token,
            )
            attachment = [('Pragyarambh_Pass.png', png_bytes, 'image/png')]
        except Exception:
            logger.exception('Failed to generate PNG pass for registration %s', registration.id)
            attachment = None
            notification_email_sent = False
            message = 'Registration approved, but pass PNG attachment could not be created.'

        if attachment is not None:
            try:
                await email_service.send_email(registration.email, subject, body, attachments=attachment)
                notification_email_sent = True
            except Exception:
                notification_email_sent = False
                message = 'Registration approved, but notification email could not be delivered.'
                logger.exception('Registration approval email delivery failed for %s', registration.email)

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

    if registration.email and email_enabled:
        subject, body = build_registration_rejection_email(registration.registration_number, payload.reason)
        try:
            await email_service.send_email(registration.email, subject, body)
            notification_email_sent = True
        except Exception:
            notification_email_sent = False
            message = 'Registration rejected, but notification email could not be delivered.'
            logger.exception('Registration rejection email delivery failed for %s', registration.email)

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


@router.post('/registrations/{registration_id}/resend-approval-email')
async def resend_approval_email(
    registration_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    registration, pass_obj, png_bytes = await _get_pass_artifact(registration_id, db)
    if registration.status != 'approved':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only approved registrations can receive an approval email')
    sent, message = await _send_approval_email(registration, pass_obj, png_bytes, email_service)
    return {
        'registration_number': registration.registration_number,
        'pass_number': pass_obj.pass_number,
        'email_sent': sent,
        'message': message,
    }
