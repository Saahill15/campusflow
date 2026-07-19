from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from repos.qr_repo import QRCodeRepository
from repos.pass_repo import PassRepository
from repos.registration_repo import RegistrationRepository
from repos.entry_log_repo import EntryLogRepository
from repos.gate_repo import GateRepository
from repos.event_settings_repo import EventSettingsRepository

from models.entry_log import EntryLog
from models.qr_code import QRCode, QRStatus
from models.pass_model import Pass, PassStatus
from models.registration import Registration, RegistrationStatus


class CheckInService:
    """Check-In Engine: validates scanned QR tokens and records EntryLogs.

    Public methods:
      - validate_qr_token(qr_token)
      - process_scan(qr_token, gate_id, scanner_id, device_identifier)
      - mark_check_in(registration, pass_obj)
    """

    # backward-compatible defaults — will be overridden by EventSettings when present
    DEFAULTS = {
        'allow_check_in': True,
        'allow_reentry': False,
        'allow_duplicate_scan': False,
        'require_active_qr': True,
        'require_active_pass': True,
        'require_approved_registration': True,
        'max_entries_per_person': 1,
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.qr_repo = QRCodeRepository(session)
        self.pass_repo = PassRepository(session)
        self.reg_repo = RegistrationRepository(session)
        self.entry_repo = EntryLogRepository(session)
        self.gate_repo = GateRepository(session)
        self.settings_repo = EventSettingsRepository(session)

    async def validate_qr_token(self, qr_token: str) -> Optional[QRCode]:
        return await self.qr_repo.get_by_token(qr_token)

    async def mark_check_in(self, registration: Registration, pass_obj: Pass) -> None:
        now = datetime.now(timezone.utc)
        registration.checked_in = True
        registration.checked_in_at = now
        pass_obj.checked_in_at = now
        self.session.add(registration)
        self.session.add(pass_obj)
        await self.session.flush()

    async def process_scan(self, qr_token: str, gate_id: str, scanner_id: Optional[int] = None, device_identifier: Optional[str] = None) -> dict:
        """Process a single scan attempt and return a structured response.

        Always creates an EntryLog recording success or failure.
        """
        now = datetime.now(timezone.utc)

        # Load gate to determine event context
        gate = await self.gate_repo.get_by_id(gate_id)
        event_id = gate.event_id if gate else None

        # load event settings if available
        settings = None
        if event_id:
            settings = await self.settings_repo.get_by_event_id(event_id)
        # map to simple config dict
        cfg = dict(self.DEFAULTS)
        if settings:
            cfg.update({
                'allow_check_in': settings.allow_check_in,
                'allow_reentry': settings.allow_reentry,
                'allow_duplicate_scan': settings.allow_duplicate_scan,
                'require_active_qr': settings.require_active_qr,
                'require_active_pass': settings.require_active_pass,
                'require_approved_registration': settings.require_approved_registration,
                'max_entries_per_person': settings.max_entries_per_person,
                'checkin_start_time': settings.checkin_start_time,
                'checkin_end_time': settings.checkin_end_time,
            })

        # default failure response
        def failure(reason: str, entry_status: str, failure_reason: Optional[str] = None, qr=None, pass_obj=None, registration=None):
            el = EntryLog(
                event_id=event_id,
                pass_id=(pass_obj.id if pass_obj else (qr.pass_id if qr else None)),
                qr_code_id=(qr.id if qr else None),
                gate_id=gate_id,
                scanned_by=scanner_id,
                entry_status=entry_status,
                failure_reason=(failure_reason or reason),
                device_identifier=device_identifier,
                scan_timestamp=now,
            )
            # create entry log and update QR counters if available
            async def _do():
                await self.entry_repo.create(el)
                if qr:
                    qr.scan_count = (qr.scan_count or 0) + 1
                    qr.last_scanned_at = now
                    self.session.add(qr)
                await self.session.commit()

            return el, _do

        # find QR
        qr = await self.qr_repo.get_by_token(qr_token)

        if not qr:
            el, fn = failure('QR missing', 'invalid', 'QR not found')
            await fn()
            return {"success": False, "reason": "QR missing"}

        # increment scan counters regardless
        qr.scan_count = (qr.scan_count or 0) + 1
        qr.last_scanned_at = now
        self.session.add(qr)

        # check QR status if required
        if cfg.get('require_active_qr', True):
            if qr.status == QRStatus.Revoked:
                el, fn = failure('QR revoked', 'revoked', 'QR revoked', qr=qr)
                await fn()
                return {"success": False, "reason": "QR revoked"}
            if qr.status == QRStatus.Expired:
                el, fn = failure('QR expired', 'expired', 'QR expired', qr=qr)
                await fn()
                return {"success": False, "reason": "QR expired"}

        # load pass
        pass_obj = await self.pass_repo.get_by_id(qr.pass_id)
        if not pass_obj:
            el, fn = failure('Pass missing', 'invalid', 'Pass not found', qr=qr)
            await fn()
            return {"success": False, "reason": "Pass missing"}

        # pass status checks if required
        if cfg.get('require_active_pass', True):
            if pass_obj.status == PassStatus.Revoked:
                el, fn = failure('Pass revoked', 'revoked', 'Pass revoked', qr=qr, pass_obj=pass_obj)
                await fn()
                return {"success": False, "reason": "Pass revoked"}
            if pass_obj.status == PassStatus.Expired:
                el, fn = failure('Pass expired', 'expired', 'Pass expired', qr=qr, pass_obj=pass_obj)
                await fn()
                return {"success": False, "reason": "Pass expired"}

        # load registration
        registration = await self.reg_repo.get_by_id(pass_obj.registration_id)
        if not registration:
            el, fn = failure('Registration missing', 'invalid', 'Registration not found', qr=qr, pass_obj=pass_obj)
            await fn()
            return {"success": False, "reason": "Registration missing"}

        # registration status checks if required
        if cfg.get('require_approved_registration', True):
            if registration.status == RegistrationStatus.Rejected:
                el, fn = failure('Registration rejected', 'rejected', 'Registration rejected', qr=qr, pass_obj=pass_obj, registration=registration)
                await fn()
                return {"success": False, "reason": "Registration rejected"}
            if registration.status == RegistrationStatus.Cancelled:
                el, fn = failure('Registration cancelled', 'rejected', 'Registration cancelled', qr=qr, pass_obj=pass_obj, registration=registration)
                await fn()
                return {"success": False, "reason": "Registration cancelled"}

        # load event via gate or registration
        event = None
        if gate:
            # event context already known
            from sqlalchemy import select
            from models.event import Event
            # load event object via session
            q = await self.session.execute(select(Event).where(Event.id == gate.event_id))
            event = q.scalars().first()

        if not event:
            # fallback to registration.event
            event = registration.event

        # check allow_check_in and event status time window
        if not cfg.get('allow_check_in', True):
            el, fn = failure('Check-in disabled for event', 'rejected', 'Check-in disabled', qr=qr, pass_obj=pass_obj, registration=registration)
            await fn()
            return {"success": False, "reason": "Check-in disabled"}

        # optional time window checks
        start_t = cfg.get('checkin_start_time')
        end_t = cfg.get('checkin_end_time')
        if start_t and now < start_t:
            el, fn = failure('Check-in not started', 'rejected', 'Check-in not started', qr=qr, pass_obj=pass_obj, registration=registration)
            await fn()
            return {"success": False, "reason": "Check-in not started"}
        if end_t and now > end_t:
            el, fn = failure('Check-in ended', 'rejected', 'Check-in ended', qr=qr, pass_obj=pass_obj, registration=registration)
            await fn()
            return {"success": False, "reason": "Check-in ended"}

        # duplicate/reentry handling based on settings
        from sqlalchemy import select, func
        q = await self.session.execute(select(func.count()).select_from(EntryLog).where(EntryLog.pass_id == pass_obj.id, EntryLog.entry_status == 'success'))
        success_count = q.scalar() or 0

        max_entries = cfg.get('max_entries_per_person', 1)

        if success_count >= max_entries:
            el, fn = failure('Duplicate entry', 'duplicate', 'Maximum entries reached', qr=qr, pass_obj=pass_obj, registration=registration)
            await fn()
            return {"success": False, "reason": "Duplicate"}

        if success_count >= 1 and not cfg.get('allow_reentry', False):
            el, fn = failure('Duplicate entry', 'duplicate', 'Registration already checked in', qr=qr, pass_obj=pass_obj, registration=registration)
            await fn()
            return {"success": False, "reason": "Duplicate"}

        # all validations passed: create success entry log, update registrations/passes/qr
        el = EntryLog(
            event_id=event.id,
            pass_id=pass_obj.id,
            qr_code_id=qr.id,
            gate_id=gate_id,
            scanned_by=scanner_id,
            entry_status='success',
            failure_reason=None,
            device_identifier=device_identifier,
            scan_timestamp=now,
        )
        await self.entry_repo.create(el)

        # mark checked in
        await self.mark_check_in(registration, pass_obj)

        # persist qr scan_count/last_scanned already set earlier
        await self.session.commit()

        # prepare response
        participant_name = getattr(registration.user, 'email', None)
        response = {
            "success": True,
            "message": "Entry Allowed",
            "entry_log_id": el.id,
            "participant_name": participant_name,
            "registration_number": registration.registration_number,
            "pass_number": pass_obj.pass_number,
        }
        return response
