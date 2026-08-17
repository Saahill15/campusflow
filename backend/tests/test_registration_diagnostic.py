from datetime import datetime, timedelta, timezone

import pytest

from app.core.config import settings
from db.session import get_session
from models.event import Event, EventStatus
from models.registration import Registration, RegistrationStatus


@pytest.mark.asyncio
async def test_registration_diagnostic_requires_token_and_reports_duplicate_counts(client, monkeypatch):
    monkeypatch.setattr(settings, 'REGISTRATION_DIAGNOSTIC_TOKEN', 'diagnostic-test-token')

    async with get_session() as session:
        event = Event(
            title='Pragyarambh 2026',
            slug='pragyarambh-2026',
            start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            end_datetime=datetime.now(timezone.utc) + timedelta(days=2),
            status=EventStatus.RegistrationOpen,
        )
        session.add(event)
        await session.flush()
        session.add(Registration(
            event_id=event.id,
            first_name='Diagnostic',
            last_name='Record',
            email='deploy-test-001@example.com',
            roll_number='DEPLOY001',
            status=RegistrationStatus.Pending,
        ))
        await session.commit()

    denied = await client.get('/api/v1/registration/diagnostic')
    assert denied.status_code == 404

    response = await client.get(
        '/api/v1/registration/diagnostic',
        headers={'X-Diagnostic-Token': 'diagnostic-test-token'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['database_connected'] is True
    assert data['pragyarambh_event_count'] == 1
    assert data['duplicate_email'] is True
    assert data['duplicate_roll'] is True
    assert data['events'][0]['registration_count'] == 1
    assert data['events'][0]['email_duplicate_count'] == 1
    assert data['events'][0]['roll_duplicate_count'] == 1
    assert 'email' not in data['events'][0]
    assert 'roll_number' not in data['events'][0]
