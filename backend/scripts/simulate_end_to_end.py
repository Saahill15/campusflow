import asyncio
from db.session import async_session
from services.registration_service import RegistrationService
# ensure model classes are imported so SQLAlchemy mapper registry is populated
import models.event
import models.registration
import models.pass_model
import models.qr_code
import models.auth

async def main():
    event_id = '19b414c5-2fa8-4827-8d40-bee0f93da44b'
    payload = {
        'first_name': 'Sim',
        'last_name': 'Tester',
        'email': 'sim.tester+e2e@example.com',
        'phone': '9999999999',
        'department': 'Testing',
        'academic_year': '2026',
    }
    async with async_session() as session:
        service = RegistrationService(session)
        reg = await service.create_registration(payload, event_id)
        print('created registration:', reg.id, reg.registration_number, reg.status)
        # approve
        approved = await service.approve_registration(reg.id, approver_user_id=1)
        print('approved:', approved.id, approved.registration_number, approved.status)

if __name__ == '__main__':
    asyncio.run(main())
