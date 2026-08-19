import pytest
from datetime import datetime, timezone
from sqlalchemy import select

from db.session import get_session
from models.auth import User
from models.event import Event
from models.registration import Registration, RegistrationStatus
from models.pass_model import Pass, PassStatus
from models.qr_code import QRCode, QRStatus
from models.gate import Gate
from models.entry_log import EntryLog
from models.system_settings import SystemSettings

from services.checkin_service import CheckInService


@pytest.mark.asyncio
async def test_checkin_success_and_counters():
    async with get_session() as s:
        # setup
        u = User(email='c1@example.com', hashed_password='x')
        scanner = User(email='scanner1@example.com', hashed_password='x')
        s.add_all([u, scanner])
        await s.flush()

        ev = Event(
            title='CheckInEvent',
            slug='checkin-1',
            start_datetime=datetime(2026, 12, 10, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 10, 12, 0, tzinfo=timezone.utc),
            status='ongoing',
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=u.id, status=RegistrationStatus.Approved)
        s.add(reg)
        await s.flush()

        p = Pass(event_id=ev.id, registration_id=reg.id, status=PassStatus.Issued, pass_number='P-CHK-001')
        s.add(p)
        await s.flush()

        qr = QRCode(pass_id=p.id, qr_token='CHK-TKN-001', status=QRStatus.Active)
        s.add(qr)
        await s.flush()

        gate = Gate(event_id=ev.id, name='Main Entrance')
        s.add(gate)
        await s.flush()

        service = CheckInService(s)

        resp = await service.process_scan('CHK-TKN-001', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-1')
        assert resp['success'] is True

        # entry log created
        q = await s.execute(select(EntryLog).where(EntryLog.id == resp['entry_log_id']))
        el = q.scalars().first()
        assert el is not None and el.entry_status == 'success'

        # registration checked in
        q = await s.execute(select(Registration).where(Registration.id == reg.id))
        reg2 = q.scalars().first()
        assert reg2.checked_in is True and reg2.checked_in_at is not None

        # qr scan count increment
        q = await s.execute(select(QRCode).where(QRCode.id == qr.id))
        qr2 = q.scalars().first()
        assert qr2.scan_count >= 1 and qr2.last_scanned_at is not None


@pytest.mark.asyncio
async def test_global_checkin_setting_blocks_scan_without_mutating_records():
    async with get_session() as s:
        ev = Event(title='DisabledCheckInEvent', slug='checkin-disabled-global', start_datetime=datetime.now(timezone.utc), end_datetime=datetime.now(timezone.utc), status='ongoing')
        s.add(ev)
        await s.flush()
        reg = Registration(event_id=ev.id, status=RegistrationStatus.Approved, checked_in=False)
        s.add(reg)
        await s.flush()
        p = Pass(event_id=ev.id, registration_id=reg.id, status=PassStatus.Issued, pass_number='P-CHK-DISABLED')
        s.add(p)
        await s.flush()
        qr = QRCode(pass_id=p.id, qr_token='CHK-DISABLED', status=QRStatus.Active, scan_count=0)
        gate = Gate(event_id=ev.id, name='Disabled Gate')
        s.add_all([qr, gate, SystemSettings(id=1, checkin_enabled=False)])
        await s.flush()

        response = await CheckInService(s).process_scan(qr.qr_token, gate.id)
        assert response == {'success': False, 'reason': 'Check-in is currently disabled.'}
        await s.refresh(reg)
        await s.refresh(qr)
        assert reg.checked_in is False
        assert qr.scan_count == 0
        assert (await s.execute(select(EntryLog).where(EntryLog.qr_code_id == qr.id))).scalars().first() is None


@pytest.mark.asyncio
async def test_duplicate_scan_and_rejections():
    async with get_session() as s:
        u = User(email='c2@example.com', hashed_password='x')
        scanner = User(email='scanner2@example.com', hashed_password='x')
        s.add_all([u, scanner])
        await s.flush()

        ev = Event(title='CheckInEvent2', slug='checkin-2', start_datetime=datetime(2026,12,11,10,0,tzinfo=timezone.utc), end_datetime=datetime(2026,12,11,12,0,tzinfo=timezone.utc), status='ongoing')
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=u.id, status=RegistrationStatus.Approved)
        s.add(reg)
        await s.flush()

        p = Pass(event_id=ev.id, registration_id=reg.id, status=PassStatus.Issued)
        s.add(p)
        await s.flush()

        qr = QRCode(pass_id=p.id, qr_token='CHK-TKN-002', status=QRStatus.Active)
        s.add(qr)
        await s.flush()

        gate = Gate(event_id=ev.id, name='Side Gate')
        s.add(gate)
        await s.flush()

        service = CheckInService(s)

        # first scan -> success
        r1 = await service.process_scan('CHK-TKN-002', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-2')
        assert r1['success'] is True

        # second scan -> duplicate
        r2 = await service.process_scan('CHK-TKN-002', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-2')
        assert r2['success'] is False and r2['reason'] == 'Duplicate'

        # revoked QR
        qr.status = QRStatus.Revoked
        s.add(qr)
        await s.flush()
        r3 = await service.process_scan('CHK-TKN-002', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-2')
        assert r3['success'] is False and r3['reason'] == 'QR revoked'

        # revoked pass
        qr.status = QRStatus.Active
        p.status = PassStatus.Revoked
        s.add_all([qr, p])
        await s.flush()
        r4 = await service.process_scan('CHK-TKN-002', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-2')
        assert r4['success'] is False and r4['reason'] == 'Pass revoked'

        # rejected registration
        p.status = PassStatus.Issued
        reg.status = RegistrationStatus.Rejected
        s.add_all([p, reg])
        await s.flush()
        r5 = await service.process_scan('CHK-TKN-002', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-2')
        assert r5['success'] is False and r5['reason'] == 'Registration rejected'

        # missing QR
        r6 = await service.process_scan('NON-EXISTENT', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-2')
        assert r6['success'] is False and r6['reason'] == 'QR missing'

        # Ensure entry logs created for attempts
        q = await s.execute(select(EntryLog).where(EntryLog.device_identifier == 'dev-2'))
        logs = q.scalars().all()
        assert len(logs) >= 5
