import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.session import get_session
from models.pass_model import Pass, PassStatus, PassType
from models.registration import Registration
from models.event import Event
from models.auth import User
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_pass_crud_and_relationships():
    async with get_session() as s:
        user = User(email='p1@example.com', hashed_password='x')
        applicant = User(email='p2@example.com', hashed_password='x')
        s.add_all([user, applicant])
        await s.flush()

        ev = Event(
            title='PassEvent',
            slug='pass-1',
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
        assert p.id is not None

        q = await s.execute(select(Pass).where(Pass.id == p.id))
        p2 = q.scalars().first()
        assert p2 is not None

        p2.is_active = False
        s.add(p2)
        await s.flush()
        q = await s.execute(select(Pass).where(Pass.id == p.id))
        p3 = q.scalars().first()
        assert not p3.is_active

        await s.delete(p3)
        await s.flush()


@pytest.mark.asyncio
async def test_pass_unique_and_enum_checks():
    async with get_session() as s:
        u = User(email='p3@example.com', hashed_password='x')
        s.add(u)
        await s.flush()

        ev = Event(
            title='PassEvent2',
            slug='pass-2',
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
        ev_id = ev.id

        p1 = Pass(event_id=ev_id, registration_id=r1_id, pass_number='P-001')
        s.add(p1)
        await s.flush()
        await s.commit()

        # duplicate pass_number should fail
        p_dup = Pass(event_id=ev_id, registration_id=r2_id, pass_number='P-001')
        s.add(p_dup)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()

        # duplicate registration -> unique constraint on registration_id
        p_same_reg = Pass(event_id=ev_id, registration_id=r1_id)
        s.add(p_same_reg)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()

        # invalid enum should fail via CHECK
        p_bad = Pass(event_id=ev_id, registration_id=r2_id, status='not_a_status')
        s.add(p_bad)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()


def test_pass_migration_runs():
    import importlib
    mod = importlib.import_module('scripts.run_alembic')
    mod
