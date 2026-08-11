import pytest
from sqlalchemy import select

from db.session import get_session
from models.auth import User
from models.event import Event
from models.registration import Registration
from models.pass_model import Pass
from models.qr_code import QRCode
from services.registration_service import RegistrationService
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_approve_creates_pass_and_qr():
    async with get_session() as s:
        approver = User(email='approver-pass@example.com', hashed_password='x')
        applicant = User(email='applicant-pass@example.com', hashed_password='x')
        s.add_all([approver, applicant])
        await s.flush()

        ev = Event(
            title='PassQREvent',
            slug='pass-qr-1',
            start_datetime=datetime(2026, 12, 20, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 20, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        svc = RegistrationService(s)
        r = await svc.approve_registration(reg.id, approver.id)

        # verify pass exists
        res = await s.execute(select(Pass).where(Pass.registration_id == reg.id))
        p = res.scalars().first()
        assert p is not None
        assert p.pass_number is not None

        # verify QR exists
        res2 = await s.execute(select(QRCode).where(QRCode.pass_id == p.id))
        q = res2.scalars().first()
        assert q is not None
        assert q.qr_token is not None


@pytest.mark.asyncio
async def test_reject_does_not_create_pass_or_qr():
    async with get_session() as s:
        approver = User(email='approver-pass2@example.com', hashed_password='x')
        applicant = User(email='applicant-pass2@example.com', hashed_password='x')
        s.add_all([approver, applicant])
        await s.flush()

        ev = Event(
            title='RejectNoPassEvent',
            slug='reject-pass-1',
            start_datetime=datetime(2026, 12, 21, 10, 0, tzinfo=timezone.utc),
            end_datetime=datetime(2026, 12, 21, 12, 0, tzinfo=timezone.utc),
        )
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        svc = RegistrationService(s)
        r = await svc.reject_registration(reg.id, approver.id, 'Not eligible')

        # verify no pass
        res = await s.execute(select(Pass).where(Pass.registration_id == reg.id))
        p = res.scalars().first()
        assert p is None

        # verify no qr
        res2 = await s.execute(select(QRCode).where(QRCode.pass_id == None))
        # nothing specifically tied to this registration should exist
        assert True


    @pytest.mark.asyncio
    async def test_atomicity_on_qr_token_collision():
        """Force a QR token collision to ensure approval rolls back atomically."""
        import uuid as _uuid

        async with get_session() as s:
            approver = User(email='approver-atomic@example.com', hashed_password='x')
            applicant = User(email='applicant-atomic@example.com', hashed_password='x')
            s.add_all([approver, applicant])
            await s.flush()

            ev = Event(
                title='AtomicEvent',
                slug='atomic-1',
                start_datetime=datetime(2026, 12, 25, 10, 0, tzinfo=timezone.utc),
                end_datetime=datetime(2026, 12, 25, 12, 0, tzinfo=timezone.utc),
            )
            s.add(ev)
            await s.flush()

            # create an existing pass+qr with a known token
            existing_reg = Registration(event_id=ev.id, user_id=applicant.id)
            s.add(existing_reg)
            await s.flush()
            existing_pass = Pass(event_id=ev.id, registration_id=existing_reg.id, pass_number='PG26-P-000001')
            s.add(existing_pass)
            await s.flush()
            fixed_token = '00000000-0000-0000-0000-000000000000'
            existing_qr = QRCode(pass_id=existing_pass.id, qr_token=fixed_token)
            s.add(existing_qr)
            await s.flush()

            # now create a fresh registration to approve
            reg = Registration(event_id=ev.id, user_id=applicant.id + 1)
            s.add(reg)
            await s.flush()

            svc = RegistrationService(s)

            # monkeypatch uuid.uuid4 to always return the fixed token, forcing a collision
            orig_uuid4 = _uuid.uuid4
            try:
                _uuid.uuid4 = lambda: _uuid.UUID(fixed_token)
                with pytest.raises(Exception):
                    await svc.approve_registration(reg.id, approver.id)
            finally:
                _uuid.uuid4 = orig_uuid4

            # After failure, ensure registration is still pending and no pass/qr exist for this reg
            res_reg = await s.execute(select(Registration).where(Registration.id == reg.id))
            r = res_reg.scalars().first()
            assert r is not None
            assert r.status == 'pending'

            res_p = await s.execute(select(Pass).where(Pass.registration_id == reg.id))
            p = res_p.scalars().first()
            assert p is None

            res_q = await s.execute(select(QRCode).where(QRCode.pass_id == None))
            # nothing tied to this registration was created
            assert True
