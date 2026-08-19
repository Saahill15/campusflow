from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.main import app
from db.session import get_session
from models.auth import Role, User
from models.system_settings import SystemSettings
from models.event import Event
from models.registration import Registration
from services.auth_service import hash_password


async def _ensure_role(session, name: str) -> Role:
    role = (await session.execute(select(Role).where(Role.name == name))).scalars().first()
    if role:
        return role
    role = Role(name=name)
    session.add(role)
    await session.flush()
    return role


async def _create_user_with_role(session, email: str, role_name: str) -> User:
    role = await _ensure_role(session, role_name)
    user = User(email=email, hashed_password=hash_password('StrongPass123'), is_active=True, is_verified=True)
    user.roles.append(role)
    session.add(user)
    await session.flush()
    return user


@pytest.mark.asyncio
async def test_default_settings_are_created_correctly(client):
    async with get_session() as session:
        settings = SystemSettings(id=1)
        session.add(settings)
        await session.commit()

    async with get_session() as session:
        saved = (await session.execute(select(SystemSettings).where(SystemSettings.id == 1))).scalars().one()
        assert saved.registration_enabled is True
        assert saved.checkin_enabled is True
        assert saved.email_enabled is True
        assert saved.maintenance_mode is False


@pytest.mark.asyncio
async def test_admin_can_get_and_patch_settings(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'settings-admin@example.com', 'admin')
        await session.commit()

    login = await client.post('/auth/login', json={'email': 'settings-admin@example.com', 'password': 'StrongPass123'})
    token = login.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    initial = await client.get('/api/v1/admin/settings', headers=headers)
    assert initial.status_code == 200
    assert initial.json() == {
        'registration_enabled': True,
        'checkin_enabled': True,
        'email_enabled': True,
        'maintenance_mode': False,
    }

    partial = await client.patch('/api/v1/admin/settings', headers=headers, json={'registration_enabled': False})
    assert partial.status_code == 200
    assert partial.json() == {
        'registration_enabled': False,
        'checkin_enabled': True,
        'email_enabled': True,
        'maintenance_mode': False,
    }

    multiple = await client.patch(
        '/api/v1/admin/settings',
        headers=headers,
        json={'checkin_enabled': False, 'email_enabled': False, 'maintenance_mode': True},
    )
    assert multiple.status_code == 200
    assert multiple.json() == {
        'registration_enabled': False,
        'checkin_enabled': False,
        'email_enabled': False,
        'maintenance_mode': True,
    }


@pytest.mark.asyncio
async def test_settings_authorization(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'settings-student@example.com', 'student')
        await session.commit()

    unauthenticated = await client.get('/api/v1/admin/settings')
    assert unauthenticated.status_code == 401

    login = await client.post('/auth/login', json={'email': 'settings-student@example.com', 'password': 'StrongPass123'})
    token = login.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    assert (await client.get('/api/v1/admin/settings', headers=headers)).status_code == 403
    assert (await client.patch('/api/v1/admin/settings', headers=headers, json={'email_enabled': False})).status_code == 403


@pytest.mark.asyncio
async def test_settings_persist_across_sessions_and_singleton_is_enforced(client):
    async with get_session() as session:
        service_settings = SystemSettings(id=1, registration_enabled=False)
        session.add(service_settings)
        await session.commit()

    async with get_session() as session:
        saved = (await session.execute(select(SystemSettings).where(SystemSettings.id == 1))).scalars().one()
        assert saved.registration_enabled is False
        assert (await session.execute(select(func.count()).select_from(SystemSettings))).scalar_one() == 1

@pytest.mark.asyncio
async def test_registration_disabled_blocks_new_submissions_but_status_and_admin_remain_available(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'settings-maintenance-admin@example.com', 'admin')
        event = Event(title='Existing Settings Event', slug='existing-settings-event', start_datetime=datetime.now(timezone.utc), end_datetime=datetime.now(timezone.utc))
        session.add(event)
        await session.flush()
        registration = Registration(event_id=event.id, email='existing-settings@example.com', registration_number='PG26-SETTINGS-1', status='pending')
        session.add_all([registration, SystemSettings(id=1, registration_enabled=False, maintenance_mode=True)])
        await session.commit()

    blocked = await client.post('/api/v1/registration', json={
        'first_name': 'New', 'last_name': 'Student', 'department': 'Cybersecurity and Digital Forensics',
        'academic_year': 'First Year', 'roll_number': 'FCSSET001', 'phone': '9876543210',
        'email': 'new-settings@example.com', 'gender': 'Male',
    })
    assert blocked.status_code == 403
    assert blocked.json()['detail'] == 'Registration is currently closed.'

    status_response = await client.post('/api/v1/registration/status', json={'email': registration.email})
    assert status_response.status_code == 200
    assert status_response.json()['found'] is True
    assert status_response.json()['registration_number'] == registration.registration_number

    login = await client.post('/auth/login', json={'email': 'settings-maintenance-admin@example.com', 'password': 'StrongPass123'})
    headers = {'Authorization': f"Bearer {login.json()['data']['access_token']}"}
    assert (await client.get('/api/v1/admin/settings', headers=headers)).status_code == 200
    disabled = await client.patch('/api/v1/admin/settings', headers=headers, json={'maintenance_mode': False, 'registration_enabled': True})
    assert disabled.status_code == 200
    assert disabled.json()['maintenance_mode'] is False

@pytest.mark.asyncio
async def test_settings_get_and_patch_persist_all_independent_flags(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'settings-independent-admin@example.com', 'admin')
        await session.commit()

    login = await client.post('/auth/login', json={'email': 'settings-independent-admin@example.com', 'password': 'StrongPass123'})
    headers = {'Authorization': f"Bearer {login.json()['data']['access_token']}"}
    response = await client.patch('/api/v1/admin/settings', headers=headers, json={'registration_enabled': False, 'checkin_enabled': True, 'email_enabled': False, 'maintenance_mode': True})
    assert response.status_code == 200
    async with get_session() as session:
        saved = (await session.execute(select(SystemSettings).where(SystemSettings.id == 1))).scalars().one()
        assert saved.registration_enabled is False
        assert saved.checkin_enabled is True
        assert saved.email_enabled is False
        assert saved.maintenance_mode is True

        duplicate = SystemSettings(id=2)
        session.add(duplicate)
        with pytest.raises(Exception):
            await session.flush()
        await session.rollback()

    async with get_session() as session:
        assert (await session.execute(select(func.count()).select_from(SystemSettings))).scalar_one() == 1
