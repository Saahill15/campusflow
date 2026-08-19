from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, select
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
from models.event import Event
from services.system_settings_service import SystemSettingsService


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

    async def dashboard_statistics(self) -> dict:
        now = datetime.now(timezone.utc)
        event = (await self.session.execute(
            select(Event)
            .where(Event.is_active.is_(True), Event.status == 'ongoing')
            .order_by(Event.start_datetime.desc())
            .limit(1)
        )).scalars().first()
        if not event:
            event = (await self.session.execute(
                select(Event)
                .where(
                    Event.is_active.is_(True),
                    Event.start_datetime <= now,
                    Event.end_datetime >= now,
                )
                .order_by(Event.start_datetime.desc())
                .limit(1)
            )).scalars().first()
        if not event:
            return {
                'event_title': None,
                'total_checked_in': 0,
                'male_checked_in': 0,
                'female_checked_in': 0,
                'other_checked_in': 0,
                'approved_eligible': 0,
                'remaining_to_check_in': 0,
            }

        successful_rows = (await self.session.execute(
            select(EntryLog.pass_id, Registration.gender)
            .join(Pass, Pass.id == EntryLog.pass_id)
            .join(Registration, Registration.id == Pass.registration_id)
            .where(EntryLog.event_id == event.id, EntryLog.entry_status == 'success')
        )).all()
        checked_in_by_pass = {pass_id: gender for pass_id, gender in successful_rows if pass_id}
        genders = [str(gender or '').strip().lower() for gender in checked_in_by_pass.values()]
        approved_eligible = (await self.session.execute(
            select(func.count()).select_from(Registration).where(
                Registration.event_id == event.id,
                Registration.status == RegistrationStatus.Approved,
            )
        )).scalar_one()
        total_checked_in = len(checked_in_by_pass)
        return {
            'event_title': event.title,
            'total_checked_in': total_checked_in,
            'male_checked_in': sum(gender == 'male' for gender in genders),
            'female_checked_in': sum(gender == 'female' for gender in genders),
            'other_checked_in': sum(gender not in {'male', 'female'} for gender in genders),
            'approved_eligible': approved_eligible,
            'remaining_to_check_in': max(approved_eligible - total_checked_in, 0),
        }

    async def preview_scan(self, qr_token: str, gate_id: str) -> dict:
        context = await self._load_scan_context(qr_token, gate_id)
        if context['status'] != 'OK':
            return context
        return self._safe_preview(context, 'ALREADY_CHECKED_IN' if context['registration'].checked_in or context['pass_obj'].checked_in_at else 'VALID_PASS')

    async def confirm_scan(self, qr_token: str, gate_id: str, scanner_id: Optional[int] = None, device_identifier: Optional[str] = None) -> dict:
        if not (await SystemSettingsService(self.session).get_settings()).checkin_enabled:
            return {'status': 'CHECKIN_DISABLED', 'message': 'Check-in is currently disabled.'}

        locked_rows = await self.session.execute(
            select(Registration, Pass).join(Pass, Pass.registration_id == Registration.id)
            .join(QRCode, QRCode.pass_id == Pass.id)
            .where(QRCode.qr_token == qr_token)
            .with_for_update()
        )
        locked_row = locked_rows.first()
        registration = locked_row[0] if locked_row else None
        context = await self._load_scan_context(qr_token, gate_id)
        if context['status'] != 'OK':
            return context
        if registration and registration.id != context['registration'].id:
            return {'status': 'ENTRY_NOT_ALLOWED', 'message': 'Entry is not allowed.'}
        registration = context['registration']
        pass_obj = context['pass_obj']
        if registration.checked_in or pass_obj.checked_in_at:
            return self._safe_preview(context, 'ALREADY_CHECKED_IN')

        successful_entries = await self.session.execute(
            select(func.count()).select_from(EntryLog).where(EntryLog.pass_id == pass_obj.id, EntryLog.entry_status == 'success')
        )
        if successful_entries.scalar_one() > 0:
            return self._safe_preview(context, 'ALREADY_CHECKED_IN')

        now = datetime.now(timezone.utc)
        entry_log = EntryLog(
            event_id=context['event'].id,
            pass_id=pass_obj.id,
            qr_code_id=context['qr'].id,
            gate_id=gate_id,
            scanned_by=scanner_id,
            entry_status='success',
            device_identifier=device_identifier,
            scan_timestamp=now,
        )
        await self.entry_repo.create(entry_log)
        registration.checked_in = True
        registration.checked_in_at = now
        pass_obj.checked_in_at = now
        self.session.add_all([registration, pass_obj])
        await self.session.commit()
        result = self._safe_preview(context, 'CHECKED_IN')
        result['entry_log_id'] = entry_log.id
        result['checked_in'] = True
        result['checked_in_at'] = now
        return result

    async def _load_scan_context(self, qr_token: str, gate_id: str) -> dict:
        if not (await SystemSettingsService(self.session).get_settings()).checkin_enabled:
            return {'status': 'CHECKIN_DISABLED', 'message': 'Check-in is currently disabled.'}

        gate = await self.gate_repo.get_by_id(gate_id)
        if not gate:
            return {'status': 'ENTRY_NOT_ALLOWED', 'message': 'Entry is not allowed.'}
        qr = await self.qr_repo.get_by_token(qr_token)
        if not qr:
            return {'status': 'INVALID_QR', 'message': 'Invalid QR.'}
        if qr.status in {QRStatus.Revoked, QRStatus.Expired} or not qr.is_active:
            return {'status': 'INVALID_QR', 'message': 'Invalid QR.'}
        pass_obj = await self.pass_repo.get_by_id(qr.pass_id)
        if not pass_obj:
            return {'status': 'PASS_NOT_FOUND', 'message': 'Pass not found.'}
        if pass_obj.status in {PassStatus.Revoked, PassStatus.Expired} or not pass_obj.is_active:
            return {'status': 'ENTRY_NOT_ALLOWED', 'message': 'Entry is not allowed.'}
        registration = await self.reg_repo.get_by_id(pass_obj.registration_id)
        if not registration or registration.status != RegistrationStatus.Approved:
            return {'status': 'ENTRY_NOT_ALLOWED', 'message': 'Entry is not allowed.'}
        event = await self.session.get(Event, gate.event_id)
        if not event or event.id != registration.event_id:
            return {'status': 'ENTRY_NOT_ALLOWED', 'message': 'Entry is not allowed.'}
        event_settings = await self.settings_repo.get_by_event_id(event.id)
        if event_settings and not event_settings.allow_check_in:
            return {'status': 'CHECKIN_DISABLED', 'message': 'Check-in is currently disabled.'}
        return {'status': 'OK', 'qr': qr, 'pass_obj': pass_obj, 'registration': registration, 'event': event}

    @staticmethod
    def _safe_preview(context: dict, result_status: str) -> dict:
        registration = context['registration']
        pass_obj = context['pass_obj']
        event = context['event']
        return {
            'status': result_status,
            'message': {
                'VALID_PASS': 'Valid pass.',
                'ALREADY_CHECKED_IN': 'This pass has already been checked in.',
                'CHECKED_IN': 'Check-in successful.',
            }.get(result_status, 'Entry is not allowed.'),
            'student_name': ' '.join(filter(None, [registration.first_name, registration.last_name])) or 'Student',
            'registration_number': registration.registration_number,
            'pass_number': pass_obj.pass_number,
            'department': registration.department,
            'academic_year': registration.academic_year,
            'event': event.title,
            'checked_in': bool(registration.checked_in or pass_obj.checked_in_at),
            'checked_in_at': registration.checked_in_at or pass_obj.checked_in_at,
        }

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

        if not (await SystemSettingsService(self.session).get_settings()).checkin_enabled:
            return {"success": False, "reason": "Check-in is currently disabled."}

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
