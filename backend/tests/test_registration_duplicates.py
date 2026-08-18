import pytest
from sqlalchemy import select

from app.main import app
from db.session import get_session
from models.event import Event, EventStatus
from models.registration import Registration
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio
async def test_new_email_and_new_roll_succeeds(client):
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "UNQ1001",
        "phone": "9999999999",
        "email": "unique1@example.com",
        "gender": "Other",
    }
    r = await client.post('/api/v1/registration', json=payload)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_same_email_different_roll_rejected(client):
    payload1 = {
        "first_name": "A",
        "last_name": "B",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "SAMEEMAIL1",
        "phone": "9999999998",
        "email": "sameemail@example.com",
        "gender": "Other",
    }
    payload2 = payload1.copy()
    payload2['roll_number'] = 'SAMEEMAIL2'

    first = await client.post('/api/v1/registration', json=payload1)
    second = await client.post('/api/v1/registration', json=payload2)
    assert first.status_code == 200
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_different_email_same_roll_rejected(client):
    payload1 = {
        "first_name": "C",
        "last_name": "D",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "SAMEROLL1",
        "phone": "9999999997",
        "email": "email.one@example.com",
        "gender": "Other",
    }
    payload2 = payload1.copy()
    payload2['email'] = 'email.two@example.com'

    first = await client.post('/api/v1/registration', json=payload1)
    second = await client.post('/api/v1/registration', json=payload2)
    assert first.status_code == 200
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_different_email_and_different_roll_succeeds(client):
    payload1 = {
        "first_name": "E",
        "last_name": "F",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "DIFF1",
        "phone": "9999999996",
        "email": "diff.one@example.com",
        "gender": "Other",
    }
    payload2 = {
        "first_name": "G",
        "last_name": "H",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "DIFF2",
        "phone": "9999999995",
        "email": "diff.two@example.com",
        "gender": "Other",
    }

    first = await client.post('/api/v1/registration', json=payload1)
    second = await client.post('/api/v1/registration', json=payload2)
    assert first.status_code == 200
    assert second.status_code == 200


@pytest.mark.asyncio
async def test_duplicate_scoped_to_pragyarambh_event(client):
    # Create another event and a registration under that event with the same email/roll
    other_email = 'scoped@example.com'
    other_roll = 'SCOPE100'

    async with get_session() as session:
        ev = Event(
            title='Other Event',
            slug='other-event',
            description='x',
            start_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            end_datetime=datetime.now(timezone.utc) + timedelta(days=2),
            status=EventStatus.Published,
        )
        session.add(ev)
        await session.flush()
        reg = Registration(event_id=ev.id, first_name='X', last_name='Y', roll_number=other_roll, email=other_email, status='pending')
        session.add(reg)
        await session.flush()

    # Posting to Pragyarambh registration endpoint should NOT consider the registration above a duplicate
    payload = {
        "first_name": "Scoped",
        "last_name": "User",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": other_roll,
        "phone": "9999999900",
        "email": other_email,
        "gender": "Other",
    }

    r = await client.post('/api/v1/registration', json=payload)
    assert r.status_code == 200
