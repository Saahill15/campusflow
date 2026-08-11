import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db.session import get_session
# Ensure model modules are imported so SQLAlchemy mappers are configured
import models.auth  # noqa: F401
import models.domain  # noqa: F401
import models.event  # noqa: F401
import models.registration  # noqa: F401
import models.pass_model  # noqa: F401
import models.qr_code  # noqa: F401
import models.gate  # noqa: F401
import models.entry_log  # noqa: F401
import models.event_settings  # noqa: F401
from models.auth import User
from models.event import Event
from models.registration import Registration
from services.registration_service import RegistrationService
from models.pass_model import Pass
from models.qr_code import QRCode
import asyncio
from datetime import datetime, timezone


async def run():
    async with get_session() as s:
        admin = User(email='manual-admin@example.com', hashed_password='x')
        applicant = User(email='manual-applicant@example.com', hashed_password='x')
        s.add_all([admin, applicant])
        await s.flush()

        ev = Event(title='ManualEvent', slug='manual-1', start_datetime=datetime(2026,12,30,10,0,tzinfo=timezone.utc), end_datetime=datetime(2026,12,30,12,0,tzinfo=timezone.utc))
        s.add(ev)
        await s.flush()

        reg = Registration(event_id=ev.id, user_id=applicant.id)
        s.add(reg)
        await s.flush()

        print('Created registration', reg.id, 'status=', reg.status)

        svc = RegistrationService(s)
        r = await svc.approve_registration(reg.id, admin.id)
        print('After approve: status=', r.status, 'approved_at=', r.approved_at)

        p = (await s.execute(__import__('sqlalchemy').select(Pass).where(Pass.registration_id == reg.id))).scalars().all()
        print('Pass count for registration:', len(p))
        if p:
            print('Pass id:', p[0].id, 'pass_number:', p[0].pass_number)
            q = (await s.execute(__import__('sqlalchemy').select(QRCode).where(QRCode.pass_id == p[0].id))).scalars().all()
            print('QR count for pass:', len(q))
            if q:
                print('QR token (masked):', str(q[0].qr_token)[:8] + '...')

        # Attempt to approve again
        try:
            await svc.approve_registration(reg.id, admin.id)
        except Exception as e:
            print('Second approve attempt error (expected):', type(e).__name__, str(e))

        p2 = (await s.execute(__import__('sqlalchemy').select(Pass).where(Pass.registration_id == reg.id))).scalars().all()
        print('Pass count after re-approve attempt:', len(p2))


if __name__ == '__main__':
    asyncio.run(run())
