import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.session import get_session
from models.registration import Registration, RegistrationStatus, PaymentStatus
from models.domain import Department, AcademicYear, Venue
from models.event import Event
from models.auth import User
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_registration_crud_and_relationships():
    async with get_session() as s:
        # create user, event and related records
        user = User(email='r1@example.com', hashed_password='x')
        dept = Department(name='CSE')
        yr = AcademicYear(code='FY')
        v = Venue(name='Hall')
        s.add_all([user, dept, yr, v])
        await s.flush()

        ev = Event(
            title='TestEvent',
            slug='testevent-1',
            start_datetime=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=user.id)
        s.add(reg)
        await s.flush()
        assert reg.id is not None

        # fetch
        q = await s.execute(select(Registration).where(Registration.id == reg.id))
        r2 = q.scalars().first()
        assert r2 is not None

        # update
        r2.notes = 'Updated note'
        s.add(r2)
        await s.flush()
        q = await s.execute(select(Registration).where(Registration.id == reg.id))
        r3 = q.scalars().first()
        assert r3.notes == 'Updated note'

        # delete
        await s.delete(r3)
        await s.flush()


@pytest.mark.asyncio
async def test_registration_unique_constraint_and_enum_checks():
    async with get_session() as s:
        user = User(email='r2@example.com', hashed_password='x')
        s.add(user)
        await s.flush()

        ev = Event(
            title='E2',
            slug='e2-reg',
            start_datetime=datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        r1 = Registration(event_id=ev.id, user_id=user.id)
        s.add(r1)
        await s.flush()

        # duplicate registration for same user+event should fail
        r2 = Registration(event_id=ev.id, user_id=user.id)
        s.add(r2)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()

        # invalid status should fail via CHECK
        r_bad = Registration(event_id=ev.id, user_id=user.id + 1, status='not_a_status')
        s.add(r_bad)
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()


def test_registration_migration_runs():
    import importlib
    mod = importlib.import_module('scripts.run_alembic')
    mod
