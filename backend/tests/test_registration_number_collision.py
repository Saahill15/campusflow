import pytest

from app.main import app
from db.session import get_session
from models.event import Event, EventStatus
from models.registration import Registration
from services.registration_number import RegistrationNumberGenerator
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio
async def test_registration_number_collision_retries(client, monkeypatch):
    async with get_session() as session:
        ev = Event(
            title='Event For RegNum Collision',
            slug='regnum-collision-event',
            description='x',
            start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            end_datetime=datetime.now(timezone.utc) + timedelta(days=2),
            status=EventStatus.Published,
        )
        session.add(ev)
        await session.flush()
        existing = Registration(
            event_id=ev.id,
            first_name='Existing',
            last_name='User',
            roll_number='COLLIDE1',
            email='collision@example.com',
            registration_number='PG26-000001',
            status='pending',
        )
        session.add(existing)
        await session.commit()

    async def fake_generate_candidate(session):
        if not hasattr(fake_generate_candidate, 'called'):
            fake_generate_candidate.called = True
            return 'PG26-000001'
        return 'PG26-000002'

    monkeypatch.setattr(RegistrationNumberGenerator, 'generate_candidate', classmethod(lambda cls, session: fake_generate_candidate(session)))

    payload = {
        'first_name': 'New',
        'last_name': 'User',
        'department': 'Dept',
        'academic_year': 'First Year',
        'roll_number': 'COLLIDE2',
        'phone': '9999999000',
        'email': 'new@example.com',
        'gender': 'Other',
    }

    response = await client.post('/api/v1/registration', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['registration_number'] == 'PG26-000002'
    assert data['registration_number'].startswith('PG26-')
