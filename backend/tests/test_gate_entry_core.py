import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.session import get_session
from models.gate import Gate
from models.entry_log import EntryLog
from models.pass_model import Pass
from models.qr_code import QRCode
from models.registration import Registration
from models.event import Event
from models.auth import User
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_gate_crud():
    async with get_session() as s:
        u = User(email='g1@example.com', hashed_password='x')
        s.add(u)
        await s.flush()

        ev = Event(
            title='GateEvent',
            slug='gate-1',
            start_datetime=datetime(2026, 12, 10, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 10, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        g = Gate(event_id=ev.id, name='Main Gate', description='Entrance A', display_order=1)
        s.add(g)
        await s.flush()
        assert g.id is not None

        q = await s.execute(select(Gate).where(Gate.id == g.id))
        g2 = q.scalars().first()
        assert g2 is not None and g2.name == 'Main Gate'

        g2.is_active = False
        s.add(g2)
        await s.flush()
        q = await s.execute(select(Gate).where(Gate.id == g.id))
        g3 = q.scalars().first()
        assert not g3.is_active

        await s.delete(g3)
        await s.flush()


@pytest.mark.asyncio
async def test_entry_log_crud_and_enum_checks():
    async with get_session() as s:
        u = User(email='e1@example.com', hashed_password='x')
        scanner = User(email='scanner@example.com', hashed_password='x')
        s.add_all([u, scanner])
        await s.flush()

        ev = Event(
            title='EntryEvent',
            slug='entry-1',
            start_datetime=datetime(2026, 12, 11, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 11, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=u.id)
        s.add(reg)
        await s.flush()

        p = Pass(event_id=ev.id, registration_id=reg.id)
        s.add(p)
        await s.flush()

        qr = QRCode(pass_id=p.id, qr_token='ENT-001')
        s.add(qr)
        await s.flush()

        gate = Gate(event_id=ev.id, name='Side Gate')
        s.add(gate)
        await s.flush()

        el = EntryLog(event_id=ev.id, pass_id=p.id, qr_code_id=qr.id, gate_id=gate.id, scanned_by=scanner.id, entry_status='success', device_identifier='dev-1', scan_timestamp=datetime.now(timezone.utc))
        s.add(el)
        await s.flush()
        assert el.id is not None

        q = await s.execute(select(EntryLog).where(EntryLog.id == el.id))
        el2 = q.scalars().first()
        assert el2 is not None and el2.entry_status == 'success'

        el2.failure_reason = 'none'
        s.add(el2)
        await s.flush()
        q = await s.execute(select(EntryLog).where(EntryLog.id == el.id))
        el3 = q.scalars().first()
        assert el3.failure_reason == 'none'

        await s.delete(el3)
        await s.flush()

        # invalid enum should fail
        el_bad = EntryLog(event_id=ev.id, entry_status='not_a_status')
        s.add(el_bad)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()


def test_entry_migration_runs():
    import importlib
    mod = importlib.import_module('scripts.run_alembic')
    mod
