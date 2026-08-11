from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from dependencies.database import get_db
import models.domain  # noqa: F401 - ensure related mappers are registered before Event queries
from models.event import Event, EventStatus
from schemas.registration import RegistrationCreate, RegistrationSubmissionResponse
from services.email_service import build_registration_confirmation_email, get_email_service
from services.registration_service import RegistrationService

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
