import pytest
from datetime import datetime, timezone

from db.session import get_session
from models.auth import User
from models.event import Event
from models.registration import Registration, RegistrationStatus
from services.registration_service import RegistrationService


@pytest.mark.asyncio
async def test_approve_registration_generates_number_and_sets_fields():
    async with get_session() as s:
        user = User(email='approver@example.com', hashed_password='x')
        applicant = User(email='applicant@example.com', hashed_password='x')
        s.add_all([user, applicant])
        await s.flush()

        ev = Event(
            title='ApproveEvent',
            slug='approve-1',
            start_datetime=datetime(2026, 12, 1, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 1, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        svc = RegistrationService(s)
        r = await svc.approve_registration(reg.id, user.id)

        assert r.status == RegistrationStatus.Approved
        assert r.approved_by == user.id
        assert r.approved_at is not None
        assert r.registration_number is not None
        assert r.registration_number.startswith('PG26-')


@pytest.mark.asyncio
async def test_reject_registration_requires_reason_and_sets_fields():
    async with get_session() as s:
        approver = User(email='approver2@example.com', hashed_password='x')
        applicant = User(email='applicant2@example.com', hashed_password='x')
        s.add_all([approver, applicant])
        await s.flush()

        ev = Event(
            title='RejectEvent',
            slug='reject-1',
            start_datetime=datetime(2026, 12, 2, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 2, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        svc = RegistrationService(s)
        with pytest.raises(ValueError):
            await svc.reject_registration(reg.id, approver.id, '')

        r = await svc.reject_registration(reg.id, approver.id, 'Incomplete details')
        assert r.status == RegistrationStatus.Rejected
        assert r.rejected_reason == 'Incomplete details'
        assert r.approved_by is None
        assert r.approved_at is None


@pytest.mark.asyncio
async def test_cannot_approve_twice_or_reject_approved():
    async with get_session() as s:
        approver = User(email='approver3@example.com', hashed_password='x')
        applicant = User(email='applicant3@example.com', hashed_password='x')
        s.add_all([approver, applicant])
        await s.flush()

        ev = Event(
            title='RepeatEvent',
            slug='repeat-1',
            start_datetime=datetime(2026, 12, 3, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 3, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        svc = RegistrationService(s)
        r = await svc.approve_registration(reg.id, approver.id)

        with pytest.raises(ValueError):
            await svc.approve_registration(reg.id, approver.id)

        with pytest.raises(ValueError):
            await svc.reject_registration(reg.id, approver.id, 'Too late')


@pytest.mark.asyncio
async def test_registration_number_uniqueness_sequence():
    async with get_session() as s:
        approver = User(email='approver4@example.com', hashed_password='x')
        a1 = User(email='a1@example.com', hashed_password='x')
        a2 = User(email='a2@example.com', hashed_password='x')
        s.add_all([approver, a1, a2])
        await s.flush()

        ev = Event(
            title='SeqEvent',
            slug='seq-1',
            start_datetime=datetime(2026, 12, 4, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 4, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        r1 = Registration(event_id=ev.id, user_id=a1.id)
        r2 = Registration(event_id=ev.id, user_id=a2.id)
        s.add_all([r1, r2])
        await s.flush()

        svc = RegistrationService(s)
        rr1 = await svc.approve_registration(r1.id, approver.id)
        rr2 = await svc.approve_registration(r2.id, approver.id)

        assert rr1.registration_number != rr2.registration_number
        assert rr1.registration_number.startswith('PG26-')
        assert rr2.registration_number.startswith('PG26-')
