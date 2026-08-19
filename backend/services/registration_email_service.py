from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.event import Event
from models.pass_model import Pass
from models.registration import Registration
from services.system_settings_service import SystemSettingsService
from services.email_service import (
    build_registration_approval_email,
    build_registration_confirmation_email,
)
from services.pdf_service import generate_pass_png_bytes
from services.qr_service import QRCodeService


async def send_confirmation_email(registration: Registration, email_service, db: AsyncSession) -> tuple[bool, str | None]:
    if not registration.email:
        return False, 'Registration has no email address.'
    if not getattr(email_service, 'enabled', False):
        return False, 'Email notifications are disabled.'
    if not (await SystemSettingsService(db).get_settings()).email_enabled:
        return False, 'Email sending is currently disabled.'

    subject, body = build_registration_confirmation_email(registration.registration_number or '')
    try:
        await email_service.send_email(registration.email, subject, body)
    except Exception:
        return False, 'Confirmation email could not be delivered.'
    return True, None


async def build_existing_pass_attachment(
    db: AsyncSession,
    registration: Registration,
    pass_obj: Pass,
) -> list[tuple[str, bytes, str]]:
    qr = await QRCodeService(db).get_by_pass(pass_obj.id)
    event_title = (
        await db.execute(select(Event.title).where(Event.id == registration.event_id))
    ).scalar_one_or_none() or 'Pragyarambh 3.0'
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
    return [('Pragyarambh_Pass.png', png_bytes, 'image/png')]


async def send_existing_pass_email(
    db: AsyncSession,
    registration: Registration,
    pass_obj: Pass,
    email_service,
) -> tuple[bool, str | None]:
    if not registration.email:
        return False, 'Registration has no email address.'
    if not getattr(email_service, 'enabled', False):
        return False, 'Email notifications are disabled.'
    if not (await SystemSettingsService(db).get_settings()).email_enabled:
        return False, 'Email sending is currently disabled.'

    try:
        attachments = await build_existing_pass_attachment(db, registration, pass_obj)
        subject, body = build_registration_approval_email(
            registration.registration_number or '',
            pass_obj.pass_number or '',
        )
        await email_service.send_email(registration.email, subject, body, attachments=attachments)
    except Exception:
        return False, 'Pass email could not be delivered.'
    return True, None
