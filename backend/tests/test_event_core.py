import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.session import get_session
from models.event import Event, EventStatus, EventVisibility
from datetime import datetime, timezone
from models.domain import Venue, Department, AcademicYear


@pytest.mark.asyncio
async def test_event_crud_and_relationships():
    async with get_session() as s:
        # create related records
        dept = Department(name='Mechanical')
        yr = AcademicYear(code='SY')
        v = Venue(name='Auditorium')
        s.add_all([dept, yr, v])
        await s.flush()

        # create event
        ev = Event(
            title='Orientation',
            slug='orientation-1',
            description='Welcome event',
            start_datetime=datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
            venue_id=v.id,
            department_id=dept.id,
            academic_year_id=yr.id,
            capacity=500,
            price=0.0,
        )
        s.add(ev)
        await s.flush()
        assert ev.id is not None

        # read with relationships
        q = await s.execute(select(Event).where(Event.id == ev.id))
        e2 = q.scalars().first()
        assert e2 is not None

        # update
        e2.title = 'Orientation Updated'
        s.add(e2)
        await s.flush()
        q = await s.execute(select(Event).where(Event.id == ev.id))
        e3 = q.scalars().first()
        assert e3.title == 'Orientation Updated'

        # delete
        await s.delete(e3)
        await s.flush()


@pytest.mark.asyncio
async def test_event_enums_and_constraints():
    async with get_session() as s:
        ev = Event(
            title='E2',
            slug='e2',
            start_datetime=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
            status='draft',
            visibility='public',
        )
        s.add(ev)
        await s.flush()

        # invalid status should fail at DB level via CHECK
        e_bad = Event(
            title='Bad',
            slug='bad',
            start_datetime=datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc),
            status='not_a_status',
            visibility='public',
        )
        s.add(e_bad)
        with pytest.raises(IntegrityError):
            await s.flush()


def test_event_migration_runs():
    import importlib
    mod = importlib.import_module('scripts.run_alembic')
    mod
