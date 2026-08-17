from datetime import datetime, timedelta, timezone
import re
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.config import settings
from dependencies.database import get_db
import models.domain  # noqa: F401 - ensure related mappers are registered before Event queries
from models.event import Event, EventStatus
from models.registration import Registration, RegistrationStatus
from schemas.registration import RegistrationCreate, RegistrationSubmissionResponse
from services.email_service import build_registration_confirmation_email, get_email_service
from services.registration_service import RegistrationService

router = APIRouter()
logger = logging.getLogger(__name__)
_DEPLOY_COMMIT_PATTERN = re.compile(r'^[0-9a-f]{7,64}$', re.IGNORECASE)
_DIAGNOSTIC_EMAIL = 'deploy-test-001@example.com'
_DIAGNOSTIC_ROLL_NUMBER = 'DEPLOY001'
_DUPLICATE_STATUSES = [
    RegistrationStatus.Pending,
    RegistrationStatus.Approved,
    RegistrationStatus.Cancelled,
    RegistrationStatus.CheckedIn,
]


async def get_or_create_pragyarambh_event(db: AsyncSession) -> Event:
    result = await db.execute(select(Event).where(Event.slug == 'pragyarambh-2026'))
    event = result.scalars().first()
    if event:
        return event

    event = Event(
        title='Pragyarambh 2026',
        slug='pragyarambh-2026',
        description='Pragyarambh 2026 registration event',
        start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
        end_datetime=datetime.now(timezone.utc) + timedelta(days=2),
        status=EventStatus.RegistrationOpen,
        requires_approval=True,
    )
    db.add(event)
    await db.flush()
    return event


def _require_diagnostic_token(x_diagnostic_token: str | None = Header(default=None)) -> None:
    configured_token = settings.REGISTRATION_DIAGNOSTIC_TOKEN
    if not configured_token or not x_diagnostic_token or not secrets.compare_digest(x_diagnostic_token, configured_token):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')


def _mask_email(value: str | None) -> str | None:
    if not value:
        return value
    local, separator, domain = value.partition('@')
    if not separator:
        return '***'
    return f"{local[:2]}***@{domain}"


def _mask_roll_number(value: str | None) -> str | None:
    if not value:
        return value
    return f'{value[:2]}***'


@router.get('/registration/diagnostic')
async def registration_diagnostic(
    _: None = Depends(_require_diagnostic_token),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Temporary, token-protected read-only production registration diagnostic."""
    normalized_email = _DIAGNOSTIC_EMAIL.strip().lower()
    normalized_roll = _DIAGNOSTIC_ROLL_NUMBER.strip().upper()

    try:
        events_count = (await db.execute(select(func.count()).select_from(Event))).scalar_one()
        registrations_count = (await db.execute(select(func.count()).select_from(Registration))).scalar_one()
        users_count = (await db.execute(text('SELECT COUNT(*) FROM users'))).scalar_one()
        matching_events = (
            await db.execute(select(Event).where(Event.slug == 'pragyarambh-2026').order_by(Event.id))
        ).scalars().all()
    except SQLAlchemyError as exc:
        logger.exception('Registration diagnostic database query failed')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Database diagnostic unavailable') from exc

    try:
        alembic_revision = (await db.execute(text('SELECT version_num FROM alembic_version LIMIT 1'))).scalar_one_or_none()
    except SQLAlchemyError:
        # The application can be run against a database created directly from metadata in tests.
        alembic_revision = None

    event_diagnostics = []
    duplicate_email = False
    duplicate_roll = False
    for event in matching_events:
        registration_count = (
            await db.execute(select(func.count()).select_from(Registration).where(Registration.event_id == event.id))
        ).scalar_one()
        email_duplicate_count = (
            await db.execute(
                select(func.count()).select_from(Registration).where(
                    Registration.event_id == event.id,
                    Registration.email == normalized_email,
                    Registration.status.in_(_DUPLICATE_STATUSES),
                )
            )
        ).scalar_one()
        roll_duplicate_count = (
            await db.execute(
                select(func.count()).select_from(Registration).where(
                    Registration.event_id == event.id,
                    Registration.roll_number == normalized_roll,
                    Registration.status.in_(_DUPLICATE_STATUSES),
                )
            )
        ).scalar_one()
        normalized_email_duplicate_count = (
            await db.execute(
                select(func.count()).select_from(Registration).where(
                    Registration.event_id == event.id,
                    func.lower(func.trim(Registration.email)) == normalized_email,
                    Registration.status.in_(_DUPLICATE_STATUSES),
                )
            )
        ).scalar_one()
        normalized_roll_duplicate_count = (
            await db.execute(
                select(func.count()).select_from(Registration).where(
                    Registration.event_id == event.id,
                    func.upper(func.trim(Registration.roll_number)) == normalized_roll,
                    Registration.status.in_(_DUPLICATE_STATUSES),
                )
            )
        ).scalar_one()
        matching_registrations = (
            await db.execute(
                select(Registration).where(
                    Registration.event_id == event.id,
                    Registration.email == normalized_email,
                    Registration.roll_number == normalized_roll,
                ).order_by(Registration.created_at, Registration.id)
            )
        ).scalars().all()
        duplicate_email = duplicate_email or email_duplicate_count > 0
        duplicate_roll = duplicate_roll or roll_duplicate_count > 0
        event_diagnostics.append({
            'event_id': event.id,
            'slug': event.slug,
            'name': event.title,
            'registration_count': registration_count,
            'email_duplicate_count': email_duplicate_count,
            'roll_duplicate_count': roll_duplicate_count,
            'normalized_email_duplicate_count': normalized_email_duplicate_count,
            'normalized_roll_duplicate_count': normalized_roll_duplicate_count,
            'matching_registrations': [],
        })
        for registration in matching_registrations:
            params = {'registration_id': registration.id}
            pass_count = (await db.execute(
                text('SELECT COUNT(*) FROM passes WHERE registration_id = :registration_id'),
                params,
            )).scalar_one()
            qrcode_count = (await db.execute(text('''
                SELECT COUNT(*)
                FROM qrcodes AS q
                JOIN passes AS p ON p.id = q.pass_id
                WHERE p.registration_id = :registration_id
            '''), params)).scalar_one()
            entry_log_count = (await db.execute(text('''
                SELECT COUNT(*)
                FROM entry_logs AS entry_log
                WHERE entry_log.pass_id IN (
                    SELECT id FROM passes WHERE registration_id = :registration_id
                )
                OR entry_log.qr_code_id IN (
                    SELECT q.id
                    FROM qrcodes AS q
                    JOIN passes AS p ON p.id = q.pass_id
                    WHERE p.registration_id = :registration_id
                )
            '''), params)).scalar_one()
            event_diagnostics[-1]['matching_registrations'].append({
                'registration_id': registration.id,
                'event_id': registration.event_id,
                'registration_number': registration.registration_number,
                'email': _mask_email(registration.email),
                'roll_number': _mask_roll_number(registration.roll_number),
                'status': registration.status,
                'payment_status': registration.payment_status,
                'created_at': registration.created_at,
                'updated_at': registration.updated_at,
                'pass_count': pass_count,
                'qrcode_count': qrcode_count,
                'entry_log_count': entry_log_count,
                'safe_to_delete': pass_count == 0 and qrcode_count == 0 and entry_log_count == 0,
            })

    response = {
        'database_connected': True,
        'alembic_revision': alembic_revision,
        'events_count': events_count,
        'registrations_count': registrations_count,
        'users_count': users_count,
        'pragyarambh_event_count': len(matching_events),
        'events': event_diagnostics,
        'duplicate_email': duplicate_email,
        'duplicate_roll': duplicate_roll,
    }
    if settings.RENDER_GIT_COMMIT and _DEPLOY_COMMIT_PATTERN.fullmatch(settings.RENDER_GIT_COMMIT):
        response['deployed_commit'] = settings.RENDER_GIT_COMMIT
    return response


@router.post('/registration', response_model=RegistrationSubmissionResponse)
async def create_registration(
    payload: RegistrationCreate,
    db: AsyncSession = Depends(get_db),
    email_service=Depends(get_email_service),
):
    service = RegistrationService(db)
    event = await get_or_create_pragyarambh_event(db)
    try:
        registration = await service.create_registration(payload.model_dump(), event.id)
    except ValueError as exc:
        detail = str(exc)
        if detail in {'duplicate_roll_number', 'duplicate_email'}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='A registration already exists for this roll number or email.') from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc

    email_enabled = getattr(email_service, 'enabled', False)
    confirmation_email_sent = False
    response_message = 'Registration submitted successfully.'

    if email_enabled:
        subject, body = build_registration_confirmation_email(registration.registration_number)
        try:
            await email_service.send_email(registration.email, subject, body)
            confirmation_email_sent = True
        except Exception:
            confirmation_email_sent = False
            response_message = 'Registration submitted successfully. Confirmation email could not be delivered at the moment.'
            logger.exception('Registration confirmation email delivery failed for %s', registration.email)
    else:
        response_message = 'Registration submitted successfully. Email notifications are disabled.'

    return RegistrationSubmissionResponse(
        registration_number=registration.registration_number,
        status=registration.status,
        email=registration.email,
        message=response_message,
        confirmation_email_sent=confirmation_email_sent,
    )

