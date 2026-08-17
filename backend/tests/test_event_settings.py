import os
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from db.session import get_session
from models.event_settings import EventSettings
from models.event import Event
from models.auth import User


@pytest.mark.asyncio
async def test_health_uses_runtime_settings(client):
    resp = await client.get('/health/')
    assert resp.status_code == 200
    payload = resp.json()
    expected_environment = os.environ.get('ENVIRONMENT', 'development')
    expected_version = os.environ.get('APP_VERSION', '1.0.0')
    assert payload['environment'] == expected_environment
    assert payload['version'] == expected_version


@pytest.mark.asyncio
async def test_event_settings_crud_and_defaults():
    async with get_session() as s:
        ev = Event(title='SettingsEvent', slug='settings-1', start_datetime=datetime(2026,12,1,tzinfo=timezone.utc), end_datetime=datetime(2026,12,2,tzinfo=timezone.utc))
        s.add(ev)
        await s.flush()

        # create with defaults
        es = EventSettings(event_id=ev.id)
        s.add(es)
        await s.flush()

        q = await s.execute(select(EventSettings).where(EventSettings.event_id == ev.id))
        es2 = q.scalars().first()
        assert es2 is not None
        assert es2.allow_check_in is True
        assert es2.allow_reentry is False
        assert es2.require_active_qr is True
        assert es2.max_entries_per_person == 1

        # update
        es2.allow_reentry = True
        es2.max_entries_per_person = 3
        s.add(es2)
        await s.flush()

        q = await s.execute(select(EventSettings).where(EventSettings.id == es2.id))
        es3 = q.scalars().first()
        assert es3.allow_reentry is True and es3.max_entries_per_person == 3

        await s.delete(es3)
        await s.flush()


@pytest.mark.asyncio
async def test_checkin_engine_reads_settings():
    async with get_session() as s:
        # setup event and settings
        ev = Event(title='CfgEvent', slug='cfg-1', start_datetime=datetime(2026,12,10,tzinfo=timezone.utc), end_datetime=datetime(2026,12,10, tzinfo=timezone.utc))
        s.add(ev)
        await s.flush()

        from models.registration import Registration, RegistrationStatus
        from models.pass_model import Pass, PassStatus
        from models.qr_code import QRCode, QRStatus
        from models.gate import Gate
        from models.auth import User
        from services.checkin_service import CheckInService

        u = User(email='cfg1@example.com', hashed_password='x')
        scanner = User(email='cfgscanner@example.com', hashed_password='x')
        s.add_all([u, scanner])
        await s.flush()

        # create settings: disable check-in
        es = EventSettings(event_id=ev.id, allow_check_in=False)
        s.add(es)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=u.id, status=RegistrationStatus.Approved)
        s.add(reg)
        await s.flush()

        p = Pass(event_id=ev.id, registration_id=reg.id, status=PassStatus.Issued)
        s.add(p)
        await s.flush()

        qr = QRCode(pass_id=p.id, qr_token='CFG-TKN-001', status=QRStatus.Active)
        s.add(qr)
        await s.flush()

        gate = Gate(event_id=ev.id, name='Cfg Gate')
        s.add(gate)
        await s.flush()

        svc = CheckInService(s)
        resp = await svc.process_scan('CFG-TKN-001', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-cfg')
        assert resp['success'] is False and resp['reason'] == 'Check-in disabled'

        # enable check-in and allow reentry and max_entries 2
        es.allow_check_in = True
        es.allow_reentry = True
        es.max_entries_per_person = 2
        s.add(es)
        await s.flush()

        r1 = await svc.process_scan('CFG-TKN-001', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-cfg')
        assert r1['success'] is True
        r2 = await svc.process_scan('CFG-TKN-001', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-cfg')
        assert r2['success'] is True
        # third scan should be duplicate now
        r3 = await svc.process_scan('CFG-TKN-001', gate_id=gate.id, scanner_id=scanner.id, device_identifier='dev-cfg')
        assert r3['success'] is False and r3['reason'] == 'Duplicate'
