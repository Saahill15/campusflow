from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import subprocess
from pathlib import Path
from fastapi.responses import JSONResponse

from dependencies.database import get_db
import models.domain  # noqa: F401 - ensure related mappers are registered before Event queries
from models.event import Event, EventStatus
from schemas.registration import RegistrationCreate, RegistrationSubmissionResponse
from services.email_service import build_registration_confirmation_email, get_email_service
from services.registration_service import RegistrationService
from services.registration_number import RegistrationNumberGenerator
from models.registration import Registration

router = APIRouter()
logger = logging.getLogger(__name__)


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



@router.post('/registration/debug')
async def registration_debug(
    payload: RegistrationCreate,
    db: AsyncSession = Depends(get_db),
    request: Request | None = None,
):
    # Strictly opt-in: require header
    if not request or not request.headers.get('X-REG-DIAG'):
        return JSONResponse({'detail': 'Diagnostics require X-REG-DIAG header.'}, status_code=403)

    event_q = await db.execute(select(Event).where(Event.slug == 'pragyarambh-2026'))
    event = event_q.scalars().first()
    if not event:
        return JSONResponse({'event_count': 0, 'message': 'Event not found'}, status_code=200)

    normalized_email = (payload.model_dump().get('email') or '').strip().lower()
    normalized_roll = (payload.model_dump().get('roll_number') or '').strip().upper()

    incoming_email_present = bool(normalized_email)
    incoming_roll_present = bool(normalized_roll)

    def _mask_email(e: str) -> str:
        if not e:
            return ''
        parts = e.split('@')
        local = parts[0]
        domain = parts[1] if len(parts) > 1 else ''
        return (local[:3] + '...' if len(local) > 3 else local) + ('@' + domain if domain else '')

    def _mask_roll(r: str) -> str:
        if not r:
            return ''
        return (r[:3] + '...' if len(r) > 3 else r)

    masked_email = _mask_email(normalized_email)
    masked_roll = _mask_roll(normalized_roll)

    email_dup_count = 0
    roll_dup_count = 0
    if incoming_email_present:
        q = await db.execute(
            select(func.count()).select_from(Registration.__table__).where(
                Registration.__table__.c.event_id == event.id,
                func.lower(func.trim(Registration.__table__.c.email)) == normalized_email,
            )
        )
        email_dup_count = int(q.scalar() or 0)
    if incoming_roll_present:
        q2 = await db.execute(
            select(func.count()).select_from(Registration.__table__).where(
                Registration.__table__.c.event_id == event.id,
                func.upper(func.trim(Registration.__table__.c.roll_number)) == normalized_roll,
            )
        )
        roll_dup_count = int(q2.scalar() or 0)

    # Next registration number candidate
    try:
        candidate = await RegistrationNumberGenerator.generate_candidate(db)
        q3 = await db.execute(select(Registration).where(Registration.registration_number == candidate))
        exists = bool(q3.scalars().first())
    except Exception:
        candidate = None
        exists = False

    # Table summary (last 20 rows)
    rows = []
    q4 = await db.execute(
        select(Registration.id, Registration.event_id, Registration.registration_number, Registration.status, Registration.email, Registration.roll_number, Registration.created_at).order_by(Registration.created_at.desc()).limit(20)
    )
    for r in q4.all():
        rid, eid, rnum, status_, email_, roll_, created = r
        # mask email/roll
        email_mask = (email_[:3] + '...') if email_ else ''
        roll_mask = (roll_[:3] + '...') if roll_ else ''
        rows.append({'id': rid, 'event_id': eid, 'registration_number': rnum, 'status': status_, 'email': email_mask, 'roll': roll_mask, 'created_at': str(created)})

    result = {
        'event_id': event.id,
        'event_slug': event.slug,
        'incoming_email_present': incoming_email_present,
        'incoming_email_normalized': masked_email,
        'incoming_roll_present': incoming_roll_present,
        'incoming_roll_normalized': masked_roll,
        'email_duplicate_count': email_dup_count,
        'roll_duplicate_count': roll_dup_count,
        'generated_registration_number': candidate,
        'registration_number_exists': exists,
        'recent_registrations_sample': rows,
    }

    return JSONResponse(result, status_code=200)


@router.post('/registration/debug-temp')
async def registration_debug_temp(
    payload: RegistrationCreate,
    db: AsyncSession = Depends(get_db),
    request: Request | None = None,
):
    # Strict opt-in header
    if not request or not request.headers.get('X-REG-DIAG-TEMP'):
        return JSONResponse({'detail': 'Diagnostics require X-REG-DIAG-TEMP header.'}, status_code=403)

    # find event
    event_q = await db.execute(select(Event).where(Event.slug == 'pragyarambh-2026'))
    event = event_q.scalars().first()
    if not event:
        return JSONResponse({'event_count': 0, 'message': 'Event not found'}, status_code=200)

    ne = (payload.model_dump().get('email') or '').strip().lower()
    nr = (payload.model_dump().get('roll_number') or '').strip().upper()

    def mask_email(e: str) -> str:
        if not e:
            return ''
        parts = e.split('@')
        local = parts[0]
        domain = parts[1] if len(parts) > 1 else ''
        return (local[:3] + '...' if len(local) > 3 else local) + ('@' + domain if domain else '')

    def mask_roll(r: str) -> str:
        if not r:
            return ''
        return (r[:3] + '...' if len(r) > 3 else r)

    email_dup_count = 0
    roll_dup_count = 0
    if ne:
        q = await db.execute(
            select(func.count()).select_from(Registration.__table__).where(
                Registration.__table__.c.event_id == event.id,
                func.lower(func.trim(Registration.__table__.c.email)) == ne,
            )
        )
        email_dup_count = int(q.scalar() or 0)
    if nr:
        q2 = await db.execute(
            select(func.count()).select_from(Registration.__table__).where(
                Registration.__table__.c.event_id == event.id,
                func.upper(func.trim(Registration.__table__.c.roll_number)) == nr,
            )
        )
        roll_dup_count = int(q2.scalar() or 0)

    # next reg number candidate and existence
    try:
        candidate = await RegistrationNumberGenerator.generate_candidate(db)
        q3 = await db.execute(select(Registration).where(Registration.registration_number == candidate))
        regnum_exists = bool(q3.scalars().first())
    except Exception:
        candidate = None
        regnum_exists = False

    # get git commit short sha from repo if available
    commit = None
    try:
        repo_root = Path(__file__).resolve().parents[2]
        out = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=str(repo_root), stderr=subprocess.DEVNULL)
        if isinstance(out, (bytes, bytearray)):
            commit = out.decode('utf-8').strip()
        else:
            commit = str(out).strip()
    except Exception:
        commit = None

    result = {
        'event_id': event.id,
        'event_slug': event.slug,
        'incoming_email_present': bool(ne),
        'incoming_email_normalized': mask_email(ne),
        'incoming_roll_present': bool(nr),
        'incoming_roll_normalized': mask_roll(nr),
        'email_duplicate_count': email_dup_count,
        'roll_duplicate_count': roll_dup_count,
        'registration_number_collision': bool(regnum_exists),
        'generated_registration_number': candidate,
        'code_commit': commit,
    }

    return JSONResponse(result, status_code=200)
