import pytest
from sqlalchemy import select

from app.main import app
from db.session import get_session
from models.registration import Registration
from services.email_service import get_email_service


class MockEmailService:
    def __init__(self, should_fail: bool = False, enabled: bool = True):
        self.should_fail = should_fail
        self.enabled = enabled
        self.calls = []

    async def send_email(self, to: str, subject: str, body: str, attachments=None) -> None:
        if not self.enabled:
            self.calls.append({'to': to, 'subject': subject, 'body': body, 'attachments': attachments, 'disabled': True})
            return
        self.calls.append({'to': to, 'subject': subject, 'body': body, 'attachments': attachments})
        if self.should_fail:
            raise RuntimeError('smtp unavailable')


@pytest.fixture
def email_service_override():
    service = MockEmailService()
    app.dependency_overrides[get_email_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_email_service, None)


@pytest.mark.asyncio
async def test_registration_creates_pending_registration(client, email_service_override):
    payload = {
        "first_name": "Asha",
        "last_name": "Rai",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "FCS26001",
        "phone": "9876543210",
        "email": "asha@example.com",
        "gender": "Female",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending'
    assert data['email'] == payload['email']
    assert data['registration_number'].startswith('PG26-')
    assert data['confirmation_email_sent'] is True
    assert len(email_service_override.calls) == 1
    call = email_service_override.calls[0]
    assert call['to'] == payload['email']
    assert data['registration_number'] in call['body']
    assert 'Pending Approval' in call['body']


@pytest.mark.asyncio
async def test_registration_kept_when_email_fails(client):
    failing_service = MockEmailService(should_fail=True)
    app.dependency_overrides[get_email_service] = lambda: failing_service

    payload = {
        "first_name": "Asha",
        "last_name": "Rai",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "FCS26002",
        "phone": "9876543210",
        "email": "asha.fail@example.com",
        "gender": "Female",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['confirmation_email_sent'] is False
    assert 'confirmation email could not be delivered' in data['message'].lower()
    assert len(failing_service.calls) == 1

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.email == payload['email']))
        registration = result.scalars().first()

    assert registration is not None
    assert registration.registration_number.startswith('PG26-')
    assert registration.status == 'pending'

    app.dependency_overrides.pop(get_email_service, None)


@pytest.mark.asyncio
async def test_registration_succeeds_when_email_disabled(client):
    disabled_service = MockEmailService(enabled=False)
    app.dependency_overrides[get_email_service] = lambda: disabled_service

    payload = {
        "first_name": "Asha",
        "last_name": "Rai",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "FCS26003",
        "phone": "9876543210",
        "email": "asha.disabled@example.com",
        "gender": "Female",
    }

    response = await client.post('/api/v1/registration', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending'
    assert data['confirmation_email_sent'] is False
    assert 'disabled' in data['message'].lower()
    assert len(disabled_service.calls) == 0

    app.dependency_overrides.pop(get_email_service, None)


@pytest.mark.asyncio
async def test_duplicate_registration_is_rejected(client, email_service_override):
    payload = {
        "first_name": "Asha",
        "last_name": "Rai",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "FCS26001",
        "phone": "9876543210",
        "email": "asha@example.com",
        "gender": "Female",
    }

    first = await client.post('/api/v1/registration', json=payload)
    second = await client.post('/api/v1/registration', json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
    assert len(email_service_override.calls) == 1


@pytest.mark.asyncio
async def test_registration_allows_reuse_after_rejection(client, email_service_override):
    payload = {
        "first_name": "Asha",
        "last_name": "Rai",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "FCS26004",
        "phone": "9876543210",
        "email": "asha.rejected@example.com",
        "gender": "Female",
    }

    first = await client.post('/api/v1/registration', json=payload)
    assert first.status_code == 200
    assert len(email_service_override.calls) == 1

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.email == payload['email']))
        registration = result.scalars().first()
        assert registration is not None
        registration.status = 'rejected'
        registration.rejected_reason = 'Not eligible'
        session.add(registration)
        await session.commit()

    second = await client.post('/api/v1/registration', json=payload)
    assert second.status_code == 200
    assert len(email_service_override.calls) == 2
    assert second.json()['status'] == 'pending'
