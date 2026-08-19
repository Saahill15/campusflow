from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from db.session import get_session
from models.auth import Role, User
from models.entry_log import EntryLog
from models.event import Event
from models.gate import Gate
from models.pass_model import Pass, PassStatus
from models.qr_code import QRCode, QRStatus
from models.registration import Registration, RegistrationStatus
from models.system_settings import SystemSettings
from services.auth_service import hash_password


async def _role(session, name: str) -> Role:
    role = (await session.execute(select(Role).where(Role.name == name))).scalars().first()
    if role:
        return role
    role = Role(name=name)
    session.add(role)
    await session.flush()
    return role


async def _user(session, email: str, role_name: str) -> User:
    role = await _role(session, role_name)
    user = User(email=email, hashed_password=hash_password('StrongPass123'), is_active=True, is_verified=True)
    user.roles.append(role)
    session.add(user)
    await session.flush()
    return user


async def _fixture(session, *, status: str = RegistrationStatus.Approved, checked_in: bool = False, suffix: str = '001', gender: str | None = None, event: Event | None = None, include_gate: bool = True):
    event = event or Event(title='Security Event', slug=f'security-{datetime.now().timestamp()}', start_datetime=datetime.now(timezone.utc), end_datetime=datetime.now(timezone.utc), status='ongoing')
    session.add(event)
    await session.flush()
    registration = Registration(event_id=event.id, first_name='Asha', last_name='Rai', department='Cybersecurity and Digital Forensics', academic_year='First Year', email=f'private-{suffix}@example.com', phone='9999999999', registration_number=f'PG26-SEC-{suffix}', gender=gender, status=status, checked_in=checked_in, checked_in_at=datetime.now(timezone.utc) if checked_in else None, notes='private admin note')
    session.add(registration)
    await session.flush()
    pass_obj = Pass(event_id=event.id, registration_id=registration.id, pass_number=f'PASS-SEC-{suffix}', status=PassStatus.Issued, checked_in_at=registration.checked_in_at)
    session.add(pass_obj)
    await session.flush()
    qr = QRCode(pass_id=pass_obj.id, qr_token=f'SEC-QR-{suffix}', status=QRStatus.Active)
    gate = Gate(event_id=event.id, name='Main Gate') if include_gate else None
    session.add(qr)
    if gate:
        session.add(gate)
    await session.flush()
    return event, registration, pass_obj, qr, gate


async def _token(client, email: str) -> str:
    response = await client.post('/auth/login', json={'email': email, 'password': 'StrongPass123'})
    return response.json()['data']['access_token']


@pytest.mark.asyncio
async def test_security_role_can_preview_and_students_cannot(client):
    async with get_session() as session:
        await _user(session, 'volunteer@example.com', 'security_volunteer')
        await _user(session, 'student-scan@example.com', 'student')
        _event, _registration, _pass, _qr, _gate = await _fixture(session, include_gate=False)
        await session.commit()

    volunteer_headers = {'Authorization': f'Bearer {await _token(client, "volunteer@example.com") }'}
    student_headers = {'Authorization': f'Bearer {await _token(client, "student-scan@example.com") }'}
    allowed = await client.post('/api/v1/security/scan', headers=volunteer_headers, json={'qr_token': 'SEC-QR-001'})
    forbidden = await client.post('/api/v1/security/scan', headers=student_headers, json={'qr_token': 'SEC-QR-001'})
    unauthenticated = await client.post('/api/v1/security/scan', json={'qr_token': 'SEC-QR-001'})
    assert allowed.status_code == 200
    assert allowed.json()['status'] == 'VALID_PASS'
    checked = await client.post('/api/v1/security/check-in', headers=volunteer_headers, json={'qr_token': 'SEC-QR-001'})
    assert checked.status_code == 200
    assert checked.json()['status'] == 'CHECKED_IN'
    assert forbidden.status_code == 403
    assert unauthenticated.status_code == 401
    assert 'email' not in allowed.text.lower()
    assert 'phone' not in allowed.text.lower()
    assert 'payment' not in allowed.text.lower()
    assert 'private admin note' not in allowed.text.lower()
    assert 'id' not in allowed.json()
    async with get_session() as session:
        entry_log = (await session.execute(select(EntryLog))).scalars().one()
        assert entry_log.gate_id is None


@pytest.mark.asyncio
async def test_security_dashboard_authorization_and_statistics(client):
    async with get_session() as session:
        await _user(session, 'dashboard-volunteer@example.com', 'security_volunteer')
        await _user(session, 'dashboard-student@example.com', 'student')
        await _user(session, 'dashboard-admin@example.com', 'admin')
        event, _male, male_pass, male_qr, gate = await _fixture(session, suffix='dash-male', gender='Male')
        _female_event, _female, female_pass, female_qr, _ = await _fixture(session, suffix='dash-female', gender='female', event=event)
        _other_event, _other, other_pass, other_qr, _ = await _fixture(session, suffix='dash-other', gender='nonbinary', event=event)
        await _fixture(session, status=RegistrationStatus.Pending, suffix='dash-pending', gender='male', event=event)
        await _fixture(session, status=RegistrationStatus.Rejected, suffix='dash-rejected', gender='female', event=event)
        await session.commit()

    volunteer_headers = {'Authorization': f'Bearer {await _token(client, "dashboard-volunteer@example.com") }'}
    student_headers = {'Authorization': f'Bearer {await _token(client, "dashboard-student@example.com") }'}
    admin_headers = {'Authorization': f'Bearer {await _token(client, "dashboard-admin@example.com") }'}
    assert (await client.get('/api/v1/security/dashboard')).status_code == 401
    assert (await client.get('/api/v1/security/dashboard', headers=student_headers)).status_code == 403
    assert (await client.get('/api/v1/security/dashboard', headers=admin_headers)).status_code == 200

    initial = await client.get('/api/v1/security/dashboard', headers=volunteer_headers)
    assert initial.json()['total_checked_in'] == 0
    assert initial.json()['approved_eligible'] == 3
    assert set(initial.json()) == {'event_title', 'total_checked_in', 'male_checked_in', 'female_checked_in', 'other_checked_in', 'approved_eligible', 'remaining_to_check_in'}

    for qr in (male_qr, female_qr, other_qr):
        preview = await client.post('/api/v1/security/scan', headers=volunteer_headers, json={'qr_token': qr.qr_token})
        assert preview.json()['status'] == 'VALID_PASS'
        checked = await client.post('/api/v1/security/check-in', headers=volunteer_headers, json={'qr_token': qr.qr_token})
        assert checked.json()['status'] == 'CHECKED_IN'
    duplicate = await client.post('/api/v1/security/check-in', headers=volunteer_headers, json={'qr_token': male_qr.qr_token})
    assert duplicate.json()['status'] == 'ALREADY_CHECKED_IN'
    failed = await client.post('/api/v1/security/scan', headers=volunteer_headers, json={'qr_token': 'missing'})
    assert failed.json()['status'] == 'INVALID_QR'

    updated = await client.get('/api/v1/security/dashboard', headers=volunteer_headers)
    assert updated.json()['total_checked_in'] == 3
    assert updated.json()['male_checked_in'] == 1
    assert updated.json()['female_checked_in'] == 1
    assert updated.json()['other_checked_in'] == 1
    assert updated.json()['remaining_to_check_in'] == 0
    assert all(field not in updated.text.lower() for field in ('email', 'phone', 'payment', 'private admin note'))
    async with get_session() as session:
        assert (await session.execute(select(func.count()).select_from(EntryLog).where(EntryLog.entry_status == 'success'))).scalar_one() == 3


@pytest.mark.asyncio
async def test_preview_is_non_mutating_and_explicit_checkin_reuses_entry_log(client):
    async with get_session() as session:
        await _user(session, 'volunteer-check@example.com', 'security_volunteer')
        _event, registration, pass_obj, qr, gate = await _fixture(session)
        await session.commit()

    headers = {'Authorization': f'Bearer {await _token(client, "volunteer-check@example.com") }'}
    preview = await client.post('/api/v1/security/scan', headers=headers, json={'qr_token': qr.qr_token})
    assert preview.json()['status'] == 'VALID_PASS'
    async with get_session() as session:
        saved = (await session.execute(select(Registration).where(Registration.id == registration.id))).scalars().one()
        assert saved.checked_in is False
        assert (await session.execute(select(func.count()).select_from(EntryLog))).scalar_one() == 0

    checked = await client.post('/api/v1/security/check-in', headers=headers, json={'qr_token': qr.qr_token})
    duplicate = await client.post('/api/v1/security/check-in', headers=headers, json={'qr_token': qr.qr_token})
    assert checked.json()['status'] == 'CHECKED_IN'
    assert duplicate.json()['status'] == 'ALREADY_CHECKED_IN'
    async with get_session() as session:
        saved = (await session.execute(select(Registration).where(Registration.id == registration.id))).scalars().one()
        saved_pass = (await session.execute(select(Pass).where(Pass.id == pass_obj.id))).scalars().one()
        assert saved.checked_in is True
        assert saved_pass.checked_in_at is not None
        assert (await session.execute(select(func.count()).select_from(EntryLog).where(EntryLog.pass_id == pass_obj.id, EntryLog.entry_status == 'success'))).scalar_one() == 1


@pytest.mark.asyncio
async def test_security_scan_result_states_and_disabled_setting(client):
    async with get_session() as session:
        await _user(session, 'volunteer-states@example.com', 'security_volunteer')
        _event, _registration, _pass, qr, gate = await _fixture(session)
        await session.commit()
    headers = {'Authorization': f'Bearer {await _token(client, "volunteer-states@example.com") }'}
    invalid = await client.post('/api/v1/security/scan', headers=headers, json={'qr_token': 'missing'})
    assert invalid.json()['status'] == 'INVALID_QR'

    async with get_session() as session:
        rejected_event, rejected, rejected_pass, rejected_qr, rejected_gate = await _fixture(session, status=RegistrationStatus.Rejected, suffix='002')
        settings = (await session.execute(select(SystemSettings).where(SystemSettings.id == 1))).scalars().first()
        if settings:
            settings.checkin_enabled = False
        else:
            session.add(SystemSettings(id=1, checkin_enabled=False))
        await session.commit()
    disabled = await client.post('/api/v1/security/scan', headers=headers, json={'qr_token': qr.qr_token})
    assert disabled.json()['status'] == 'CHECKIN_DISABLED'
    assert rejected_event and rejected and rejected_pass and rejected_qr and rejected_gate


@pytest.mark.asyncio
async def test_security_volunteer_cannot_use_admin_or_settings_endpoints(client):
    async with get_session() as session:
        await _user(session, 'volunteer-boundary@example.com', 'security_volunteer')
        await _fixture(session)
        await session.commit()
    headers = {'Authorization': f'Bearer {await _token(client, "volunteer-boundary@example.com") }'}
    assert (await client.get('/api/v1/admin/settings', headers=headers)).status_code == 403
    assert (await client.get('/api/v1/admin/registrations', headers=headers)).status_code == 403
    assert (await client.post('/api/v1/admin/registrations/not-real/approve', headers=headers)).status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_scanner_without_security_role(client):
    async with get_session() as session:
        await _user(session, 'scanner-admin@example.com', 'admin')
        _event, _registration, _pass, _qr, gate = await _fixture(session, suffix='003')
        await session.commit()
    headers = {'Authorization': f'Bearer {await _token(client, "scanner-admin@example.com") }'}
    response = await client.post('/api/v1/security/scan', headers=headers, json={'qr_token': 'SEC-QR-003'})
    assert response.status_code == 200
    assert response.json()['status'] == 'VALID_PASS'


@pytest.mark.asyncio
async def test_admin_can_manage_security_volunteers_without_exposing_hashes(client):
    async with get_session() as session:
        await _user(session, 'volunteer-admin@example.com', 'admin')
        await session.commit()
    headers = {'Authorization': f'Bearer {await _token(client, "volunteer-admin@example.com") }'}
    created = await client.post('/api/v1/admin/security-volunteers', headers=headers, json={
        'email': 'new-volunteer@example.com', 'password': 'StrongPass123', 'confirm_password': 'StrongPass123',
    })
    assert created.status_code == 201
    assert created.json()['email'] == 'new-volunteer@example.com'
    assert 'hashed_password' not in created.json()
    assert 'password' not in created.json()

    listed = await client.get('/api/v1/admin/security-volunteers', headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]['email'] == 'new-volunteer@example.com'
    assert all('hashed_password' not in item and 'password' not in item for item in listed.json())

    user_id = created.json()['id']
    deactivated = await client.patch(f'/api/v1/admin/security-volunteers/{user_id}', headers=headers, json={'is_active': False})
    assert deactivated.status_code == 200
    assert deactivated.json()['is_active'] is False
    assert (await client.post('/auth/login', json={'email': 'new-volunteer@example.com', 'password': 'StrongPass123'})).status_code == 401


@pytest.mark.asyncio
async def test_only_admins_can_manage_security_volunteers_and_creation_validates(client):
    async with get_session() as session:
        await _user(session, 'volunteer-student@example.com', 'student')
        await _user(session, 'volunteer-admin-two@example.com', 'admin')
        await session.commit()
    student_headers = {'Authorization': f'Bearer {await _token(client, "volunteer-student@example.com") }'}
    admin_headers = {'Authorization': f'Bearer {await _token(client, "volunteer-admin-two@example.com") }'}
    assert (await client.get('/api/v1/admin/security-volunteers', headers=student_headers)).status_code == 403
    assert (await client.post('/api/v1/admin/security-volunteers', headers=student_headers, json={'email': 'blocked@example.com', 'password': 'StrongPass123', 'confirm_password': 'StrongPass123'})).status_code == 403
    mismatch = await client.post('/api/v1/admin/security-volunteers', headers=admin_headers, json={'email': 'mismatch@example.com', 'password': 'StrongPass123', 'confirm_password': 'Different123'})
    invalid = await client.post('/api/v1/admin/security-volunteers', headers=admin_headers, json={'email': 'not-an-email', 'password': 'StrongPass123', 'confirm_password': 'StrongPass123'})
    assert mismatch.status_code == 422
    assert invalid.status_code == 422
    created = await client.post('/api/v1/admin/security-volunteers', headers=admin_headers, json={'email': 'duplicate@example.com', 'password': 'StrongPass123', 'confirm_password': 'StrongPass123'})
    duplicate = await client.post('/api/v1/admin/security-volunteers', headers=admin_headers, json={'email': 'duplicate@example.com', 'password': 'StrongPass123', 'confirm_password': 'StrongPass123'})
    assert created.status_code == 201
    assert duplicate.status_code == 409
