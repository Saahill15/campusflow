import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.session import get_session
from models.qr_code import QRCode, QRStatus
from models.pass_model import Pass
from models.registration import Registration
from models.event import Event
from models.auth import User
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_qr_crud_and_relationships():
    async with get_session() as s:
        user = User(email='qr1@example.com', hashed_password='x')
        applicant = User(email='qr2@example.com', hashed_password='x')
        s.add_all([user, applicant])
        await s.flush()

        ev = Event(
            title='QREvent',
            slug='qr-1',
            start_datetime=datetime(2026, 12, 10, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 10, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        p = Pass(event_id=ev.id, registration_id=reg.id)
        s.add(p)
        await s.flush()

        q = QRCode(pass_id=p.id)
        s.add(q)
        await s.flush()
        assert q.id is not None

        q2 = (await s.execute(select(QRCode).where(QRCode.id == q.id))).scalars().first()
        assert q2 is not None

        q2.scan_count = 5
        s.add(q2)
        await s.flush()
        q3 = (await s.execute(select(QRCode).where(QRCode.id == q.id))).scalars().first()
        assert q3.scan_count == 5

        await s.delete(q3)
        await s.flush()


@pytest.mark.asyncio
async def test_qr_unique_and_enum_checks():
    async with get_session() as s:
        u = User(email='qr3@example.com', hashed_password='x')
        s.add(u)
        await s.flush()

        ev = Event(
            title='QREvent2',
            slug='qr-2',
            start_datetime=datetime(2026, 12, 11, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 11, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        r1 = Registration(event_id=ev.id, user_id=u.id)
        r2 = Registration(event_id=ev.id, user_id=u.id + 1)
        s.add_all([r1, r2])
        await s.flush()
        r1_id = r1.id
        r2_id = r2.id

        p1 = Pass(event_id=ev.id, registration_id=r1_id)
        p2 = Pass(event_id=ev.id, registration_id=r2_id)
        s.add_all([p1, p2])
        await s.flush()
        p1_id = p1.id
        p2_id = p2.id

        qr1 = QRCode(pass_id=p1_id, qr_token='TKN-001')
        s.add(qr1)
        await s.flush()
        await s.commit()

        # duplicate token should fail
        qr_dup = QRCode(pass_id=p2_id, qr_token='TKN-001')
        s.add(qr_dup)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()

        # duplicate pass -> unique constraint on pass_id
        qr_same = QRCode(pass_id=p1_id)
        s.add(qr_same)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()

        # invalid enum should fail via CHECK
        qr_bad = QRCode(pass_id=p2_id, status='not_a_status')
        s.add(qr_bad)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()


def test_qr_migration_runs():
    import importlib
    mod = importlib.import_module('scripts.run_alembic')
    mod
