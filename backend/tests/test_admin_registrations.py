from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.main import app
from db.session import get_session
from models.auth import Role, User
from models.event import Event
from models.pass_model import Pass, PassStatus
from models.qr_code import QRCode, QRStatus
from models.registration import PaymentStatus, Registration
from services import registration_service
from services.auth_service import hash_password
from services.email_service import (
    build_registration_approval_email,
    build_registration_confirmation_email,
    get_email_service,
)


class MockEmailService:
    def __init__(self, should_fail: bool = False, enabled: bool = True):
        self.should_fail = should_fail
        self.enabled = enabled
        self.calls = []

    async def send_email(self, to: str, subject: str, body: str, attachments=None) -> None:
        self.calls.append({'to': to, 'subject': subject, 'body': body, 'attachments': attachments, 'enabled': self.enabled})
        if not self.enabled:
            return
        if self.should_fail:
            raise RuntimeError('smtp unavailable')


@pytest.fixture
def email_service_override():
    service = MockEmailService()
    app.dependency_overrides[get_email_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_email_service, None)


async def _ensure_role(session, name: str) -> Role:
    result = await session.execute(select(Role).where(Role.name == name))
    role = result.scalars().first()
    if role:
        return role
    role = Role(name=name)
    session.add(role)
    await session.flush()
    return role


async def _create_user_with_role(session, email: str, password: str, role_name: str) -> User:
    role = await _ensure_role(session, role_name)
    user = User(email=email, hashed_password=hash_password(password), is_active=True, is_verified=True)
    user.roles.append(role)
    session.add(user)
    await session.flush()
    return user


async def _create_registration(session, registration_number: str, email: str, status: str = 'pending') -> Registration:
    event = Event(
        title='Admin Test Event',
        slug=f'admin-test-{registration_number.lower()}',
        start_datetime=datetime(2026, 8, 12, 10, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc),
    )
    session.add(event)
    await session.flush()

    registration = Registration(
        event_id=event.id,
        user_id=None,
        first_name='Asha',
        last_name='Rai',
        department='Cybersecurity and Digital Forensics',
        academic_year='First Year',
        roll_number='FCS26001',
        phone='9876543210',
        email=email,
        gender='Female',
        registration_number=registration_number,
        status=status,
    )
    session.add(registration)
    await session.flush()
    return registration


async def _create_pass_and_qr(session, registration: Registration):
    p = Pass(
        event_id=registration.event_id,
        registration_id=registration.id,
        pass_number='PG26-P-000010',
        status=PassStatus.Issued,
        issued_at=datetime.now(timezone.utc),
    )
    session.add(p)
    await session.flush()

    q = QRCode(
        pass_id=p.id,
        qr_token='TESTQR-0001',
        status=QRStatus.Active,
        generated_at=datetime.now(timezone.utc),
    )
    session.add(q)
    await session.flush()
    return p, q


@pytest.mark.asyncio
async def test_admin_login_succeeds_with_valid_credentials(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin@example.com', 'StrongPass123', 'admin')
        await session.commit()

    response = await client.post('/auth/login', json={'email': 'admin@example.com', 'password': 'StrongPass123'})
    assert response.status_code == 200
    data = response.json()['data']
    assert 'access_token' in data
    assert 'refresh_token' in data

    me_response = await client.get('/auth/me', headers={'Authorization': f"Bearer {data['access_token']}"})
    assert me_response.status_code == 200
    me_data = me_response.json()['data']
    assert 'admin' in me_data['roles']


@pytest.mark.asyncio
async def test_invalid_admin_login_fails(client):
    response = await client.post('/auth/login', json={'email': 'missing@example.com', 'password': 'WrongPass123'})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_registrations_access_control(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'student@example.com', 'StrongPass123', 'student')
        await _create_user_with_role(session, 'admin2@example.com', 'StrongPass123', 'admin')
        await _create_registration(session, 'PG26-000001', 'student.one@example.com')
        await session.commit()

    unauthenticated = await client.get('/api/v1/admin/registrations')
    assert unauthenticated.status_code == 401

    student_login = await client.post('/auth/login', json={'email': 'student@example.com', 'password': 'StrongPass123'})
    student_token = student_login.json()['data']['access_token']
    forbidden = await client.get('/api/v1/admin/registrations', headers={'Authorization': f'Bearer {student_token}'})
    assert forbidden.status_code == 403

    admin_login = await client.post('/auth/login', json={'email': 'admin2@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    allowed = await client.get('/api/v1/admin/registrations', headers={'Authorization': f'Bearer {admin_token}'})
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload['meta']['total'] == 1
    item = payload['items'][0]
    assert item['registration_number'] == 'PG26-000001'
    assert item['first_name'] == 'Asha'
    assert item['last_name'] == 'Rai'
    assert item['department'] == 'Cybersecurity and Digital Forensics'
    assert item['academic_year'] == 'First Year'
    assert item['roll_number'] == 'FCS26001'
    assert item['phone'] == '9876543210'
    assert item['email'] == 'student.one@example.com'
    assert item['gender'] == 'Female'
    assert item['status'] == 'pending'
    assert 'hashed_password' not in item
    assert 'token' not in item


@pytest.mark.asyncio
async def test_admin_dashboard_summary_returns_overview_counts(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'dashboard-admin@example.com', 'StrongPass123', 'admin')
        await _create_user_with_role(session, 'dashboard-student@example.com', 'StrongPass123', 'student')

        pending = await _create_registration(session, 'PG26-D-000001', 'dashboard.pending@example.com', status='pending')
        approved = await _create_registration(session, 'PG26-D-000002', 'dashboard.approved@example.com', status='approved')
        approved.checked_in = True
        approved.payment_status = PaymentStatus.Verified
        approved.department = 'Artificial Intelligence and Machine Learning'
        approved.academic_year = 'Second Year'
        rejected = await _create_registration(session, 'PG26-D-000003', 'dashboard.rejected@example.com', status='rejected')
        rejected.payment_status = PaymentStatus.Pending
        rejected.department = 'Data Science and Data Analysis'
        rejected.academic_year = 'Third Year'
        pending.payment_status = PaymentStatus.NotRequired
        pending.created_at = datetime(2026, 8, 12, 10, 0, tzinfo=timezone.utc)
        approved.created_at = datetime(2026, 8, 12, 11, 0, tzinfo=timezone.utc)
        rejected.created_at = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'dashboard-admin@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.get(
        '/api/v1/admin/dashboard/summary',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['total_registrations'] == 3
    assert data['pending_approval'] == 1
    assert data['approved'] == 1
    assert data['rejected'] == 1
    assert data['checked_in'] == 1
    assert data['not_checked_in'] == 2
    assert {item['label']: item['count'] for item in data['payment_overview']} == {
        'Paid': 1,
        'Pending': 1,
        'Not Required': 1,
    }
    assert data['recent_registrations'][0]['registration_number'] == 'PG26-D-000003'
    assert {item['label']: item['count'] for item in data['department_overview']} == {
        'Cybersecurity and Digital Forensics': 1,
        'Artificial Intelligence and Machine Learning': 1,
        'Data Science and Data Analysis': 1,
    }
    assert {item['label']: item['count'] for item in data['academic_year_overview']} == {
        'First Year': 1,
        'Second Year': 1,
        'Third Year': 1,
    }

    student_login = await client.post('/auth/login', json={'email': 'dashboard-student@example.com', 'password': 'StrongPass123'})
    student_token = student_login.json()['data']['access_token']
    forbidden = await client.get(
        '/api/v1/admin/dashboard/summary',
        headers={'Authorization': f'Bearer {student_token}'},
    )
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_admin_registration_detail_returns_full_fields(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin3@example.com', 'StrongPass123', 'admin')
        await _create_user_with_role(session, 'student.detail@example.com', 'StrongPass123', 'student')
        registration = await _create_registration(session, 'PG26-000002', 'student.two@example.com', status='approved')
        registration.payment_status = PaymentStatus.Verified
        registration.payment_mode = 'UPI'
        registration.payment_amount = 250.0
        registration.payment_reference = 'UPI-DETAIL-0002'
        registration.payment_proof = 'data:image/png;base64,proof'
        registration.checked_in = True
        registration.checked_in_at = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin3@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    detail = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert detail.status_code == 200
    data = detail.json()
    assert data['registration_number'] == 'PG26-000002'
    assert data['status'] == 'approved'
    assert data['first_name'] == 'Asha'
    assert data['last_name'] == 'Rai'
    assert data['department'] == 'Cybersecurity and Digital Forensics'
    assert data['academic_year'] == 'First Year'
    assert data['roll_number'] == 'FCS26001'
    assert data['phone'] == '9876543210'
    assert data['email'] == 'student.two@example.com'
    assert data['gender'] == 'Female'
    assert data['payment_status'] == 'verified'
    assert data['payment_mode'] == 'UPI'
    assert data['payment_amount'] == 250.0
    assert data['payment_reference'] == 'UPI-DETAIL-0002'
    assert data['payment_proof'] == 'data:image/png;base64,proof'
    assert data['checked_in'] is True
    assert data['checked_in_at'] is not None

    student_login = await client.post('/auth/login', json={'email': 'student.detail@example.com', 'password': 'StrongPass123'})
    student_token = student_login.json()['data']['access_token']
    forbidden = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {student_token}'})
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_admin_registration_list_supports_stage_1b_filters_and_pass_data(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage1b-admin@example.com', 'StrongPass123', 'admin')
        await _create_user_with_role(session, 'stage1b-student@example.com', 'StrongPass123', 'student')

        pending = await _create_registration(session, 'PG26-B-000001', 'stage1b.pending@example.com', status='pending')
        pending.payment_status = PaymentStatus.Pending
        pending.created_at = datetime(2026, 8, 11, 10, 0, tzinfo=timezone.utc)

        approved = await _create_registration(session, 'PG26-B-000002', 'stage1b.approved@example.com', status='approved')
        approved.department = 'Artificial Intelligence and Machine Learning'
        approved.academic_year = 'Second Year'
        approved.checked_in = True
        approved.payment_status = PaymentStatus.Verified
        approved.created_at = datetime(2026, 8, 12, 10, 0, tzinfo=timezone.utc)
        pass_obj, _ = await _create_pass_and_qr(session, approved)
        pass_obj.pass_number = 'PG26-B-PASS-000002'

        rejected = await _create_registration(session, 'PG26-B-000003', 'stage1b.rejected@example.com', status='rejected')
        rejected.department = 'Data Science and Data Analysis'
        rejected.academic_year = 'Third Year'
        rejected.payment_status = PaymentStatus.Rejected
        rejected.created_at = datetime(2026, 8, 13, 10, 0, tzinfo=timezone.utc)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'stage1b-admin@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {admin_token}'}

    base = await client.get('/api/v1/admin/registrations?per_page=2', headers=headers)
    assert base.status_code == 200
    assert base.json()['meta'] == {'total': 3, 'page': 1, 'per_page': 2}
    assert base.json()['items'][0]['registration_number'] == 'PG26-B-000003'
    assert base.json()['filters']['payment_statuses'] == ['not_required', 'pending', 'verified', 'rejected']

    pass_search = await client.get('/api/v1/admin/registrations?search=PG26-B-PASS-000002', headers=headers)
    assert [item['registration_number'] for item in pass_search.json()['items']] == ['PG26-B-000002']
    pass_item = pass_search.json()['items'][0]
    assert pass_item['pass_number'] == 'PG26-B-PASS-000002'
    assert pass_item['pass_status'] == 'issued'
    assert pass_item['checked_in'] is True

    filter_cases = [
        ('status=approved', ['PG26-B-000002']),
        ('payment_status=pending', ['PG26-B-000001']),
        ('department=Data%20Science%20and%20Data%20Analysis', ['PG26-B-000003']),
        ('academic_year=Second%20Year', ['PG26-B-000002']),
        ('checked_in=true', ['PG26-B-000002']),
        ('checked_in=false', ['PG26-B-000003', 'PG26-B-000001']),
        ('date_from=2026-08-13&date_to=2026-08-13', ['PG26-B-000003']),
    ]
    for query, registration_numbers in filter_cases:
        response = await client.get(f'/api/v1/admin/registrations?{query}', headers=headers)
        assert response.status_code == 200
        assert [item['registration_number'] for item in response.json()['items']] == registration_numbers

    student_login = await client.post('/auth/login', json={'email': 'stage1b-student@example.com', 'password': 'StrongPass123'})
    student_token = student_login.json()['data']['access_token']
    forbidden = await client.get('/api/v1/admin/registrations?payment_status=verified', headers={'Authorization': f'Bearer {student_token}'})
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_approve_pending_registration(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin4@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000003', 'student.three@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin4@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(f'/api/v1/admin/registrations/{registration.id}/approve', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    data = response.json()
    assert data['registration_number'] == 'PG26-000003'
    assert data['status'] == 'approved'
    assert data['approved_at'] is not None

    detail = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert detail.status_code == 200
    detail_data = detail.json()
    assert detail_data['status'] == 'approved'
    assert detail_data['approved_at'] is not None
    assert detail_data['rejected_reason'] is None


@pytest.mark.asyncio
async def test_admin_approval_sends_notification_email(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin11@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000013', 'student.approve@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin11@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/approve',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['notification_email_sent'] is True
    assert data['message'] is None
    assert len(email_service_override.calls) == 1
    assert email_service_override.calls[0]['to'] == 'student.approve@example.com'
    assert 'Registration Approved' in email_service_override.calls[0]['body']
    assert registration.registration_number in email_service_override.calls[0]['body']
    assert 'Pass Number:' in email_service_override.calls[0]['body']
    assert 'QR Token' not in email_service_override.calls[0]['body']
    assert email_service_override.calls[0]['attachments'] is not None
    assert len(email_service_override.calls[0]['attachments']) == 1
    filename, content, content_type = email_service_override.calls[0]['attachments'][0]
    assert filename.endswith('.png')
    assert content_type == 'image/png'
    assert isinstance(content, (bytes, bytearray))


@pytest.mark.asyncio
async def test_admin_approval_succeeds_when_email_disabled(client):
    disabled_service = MockEmailService(enabled=False)
    app.dependency_overrides[get_email_service] = lambda: disabled_service

    async with get_session() as session:
        await _create_user_with_role(session, 'admin13@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000015', 'student.disabled@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin13@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/approve',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['notification_email_sent'] is False
    assert 'disabled' in data['message'].lower()
    assert len(disabled_service.calls) == 0

    app.dependency_overrides.pop(get_email_service, None)


@pytest.mark.asyncio
async def test_admin_rejection_succeeds_when_email_disabled(client):
    disabled_service = MockEmailService(enabled=False)
    app.dependency_overrides[get_email_service] = lambda: disabled_service

    async with get_session() as session:
        await _create_user_with_role(session, 'admin14@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000016', 'student.disabled2@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin14@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': 'Not eligible'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['notification_email_sent'] is False
    assert 'disabled' in data['message'].lower()
    assert len(disabled_service.calls) == 0

    app.dependency_overrides.pop(get_email_service, None)


@pytest.mark.asyncio
async def test_admin_already_approved_does_not_send_second_email(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin15@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000017', 'student.repeatapprove@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin15@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']

    first = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/approve',
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    assert first.status_code == 200

    second = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/approve',
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    assert second.status_code == 400
    assert len(email_service_override.calls) == 1


@pytest.mark.asyncio
async def test_admin_already_rejected_does_not_send_second_email(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin16@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000018', 'student.repeatreject@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin16@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']

    first = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': 'Incomplete details'},
    )
    assert first.status_code == 200

    second = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': 'Still incomplete'},
    )
    assert second.status_code == 400
    assert len(email_service_override.calls) == 1


@pytest.mark.asyncio
async def test_admin_approval_pass_qr_failure_does_not_send_email(client):
    failing_service = MockEmailService(enabled=True)
    app.dependency_overrides[get_email_service] = lambda: failing_service

    import uuid
    from unittest.mock import patch

    async with get_session() as session:
        await _create_user_with_role(session, 'admin17@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000019', 'student.failqr@example.com', status='pending')
        await session.commit()

    # Insert an existing QR token collision to force failure in approve_registration
    async with get_session() as session:
        existing_registration = await _create_registration(session, 'PG26-000020', 'student.existing@example.com', status='approved')
        existing_pass = Pass(event_id=existing_registration.event_id, registration_id=existing_registration.id, pass_number='PG26-P-000100', status=PassStatus.Issued)
        session.add(existing_pass)
        await session.flush()
        existing_qr = QRCode(pass_id=existing_pass.id, qr_token='00000000-0000-0000-0000-000000000000', status=QRStatus.Active)
        session.add(existing_qr)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin17@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']

    with patch.object(registration_service.uuid, 'uuid4', return_value=uuid.UUID('00000000-0000-0000-0000-000000000000')):
        response = await client.post(
            f'/api/v1/admin/registrations/{registration.id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'},
        )

    assert response.status_code == 400
    assert len(failing_service.calls) == 0

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.id == registration.id))
        actual = result.scalars().first()
    assert actual is not None
    assert actual.status == 'pending'

    app.dependency_overrides.pop(get_email_service, None)


@pytest.mark.asyncio
async def test_admin_rejection_sends_notification_email(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin12@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000014', 'student.reject@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin12@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': 'Does not meet requirements'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['notification_email_sent'] is True
    assert data['message'] is None
    assert len(email_service_override.calls) == 1
    assert email_service_override.calls[0]['to'] == 'student.reject@example.com'
    assert 'Registration Rejected' in email_service_override.calls[0]['body']
    assert 'Does not meet requirements' in email_service_override.calls[0]['body']


@pytest.mark.asyncio
async def test_admin_can_get_registration_pass_with_qr(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'adminpass@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000011', 'student.pass@example.com', status='approved')
        p, q = await _create_pass_and_qr(session, registration)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'adminpass@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.get(
        f'/api/v1/admin/registrations/{registration.id}/pass',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == p.id
    assert data['pass_number'] == p.pass_number
    assert data['status'] == 'issued'
    assert data['qr']['qr_token'] == q.qr_token


@pytest.mark.asyncio
async def test_admin_get_registration_pass_returns_404_when_pass_missing(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'adminpass2@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000012', 'student.nopass@example.com', status='approved')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'adminpass2@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.get(
        f'/api/v1/admin/registrations/{registration.id}/pass',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_download_existing_pass_without_creating_another(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'download-admin@example.com', 'StrongPass123', 'admin')
        await _create_user_with_role(session, 'download-student@example.com', 'StrongPass123', 'student')
        registration = await _create_registration(session, 'PG26-DL-000001', 'download.student@example.com', status='approved')
        pass_obj, _ = await _create_pass_and_qr(session, registration)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'download-admin@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = await client.get(f'/api/v1/admin/registrations/{registration.id}/pass/download', headers=headers)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    assert 'Pragyarambh_Pass.png' in response.headers['content-disposition']
    assert response.content.startswith(b'\x89PNG')

    async with get_session() as session:
        passes = (await session.execute(select(Pass).where(Pass.registration_id == registration.id))).scalars().all()
        qrs = (await session.execute(select(QRCode).where(QRCode.pass_id == pass_obj.id))).scalars().all()
    assert len(passes) == 1
    assert len(qrs) == 1

    student_login = await client.post('/auth/login', json={'email': 'download-student@example.com', 'password': 'StrongPass123'})
    student_token = student_login.json()['data']['access_token']
    forbidden = await client.get(f'/api/v1/admin/registrations/{registration.id}/pass/download', headers={'Authorization': f'Bearer {student_token}'})
    assert forbidden.status_code == 403
    unauthenticated = await client.get(f'/api/v1/admin/registrations/{registration.id}/pass/download')
    assert unauthenticated.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_resend_approval_email_using_existing_pass_and_qr(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'resend-admin@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-RESEND-000001', 'resend.student@example.com', status='approved')
        pass_obj, qr_obj = await _create_pass_and_qr(session, registration)
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'resend-admin@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/resend-approval-email',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['email_sent'] is True
    assert data['pass_number'] == pass_obj.pass_number
    assert len(email_service_override.calls) == 1
    assert email_service_override.calls[0]['attachments'][0][0] == 'Pragyarambh_Pass.png'
    assert email_service_override.calls[0]['attachments'][0][2] == 'image/png'

    async with get_session() as session:
        passes = (await session.execute(select(Pass).where(Pass.registration_id == registration.id))).scalars().all()
        qrs = (await session.execute(select(QRCode).where(QRCode.pass_id == qr_obj.pass_id))).scalars().all()
    assert len(passes) == 1
    assert len(qrs) == 1


@pytest.mark.asyncio
async def test_admin_can_reject_pending_registration(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin5@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000004', 'student.four@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin5@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': 'Invalid registration details'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['registration_number'] == 'PG26-000004'
    assert data['status'] == 'rejected'
    assert data['rejected_reason'] == 'Invalid registration details'

    detail = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert detail.status_code == 200
    detail_data = detail.json()
    assert detail_data['status'] == 'rejected'
    assert detail_data['rejected_reason'] == 'Invalid registration details'
    assert detail_data['approved_by'] is None
    assert detail_data['approved_at'] is None


@pytest.mark.asyncio
async def test_rejection_requires_a_reason(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin6@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000005', 'student.five@example.com', status='pending')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin6@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': ''},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_normal_user_cannot_approve_or_reject(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'student2@example.com', 'StrongPass123', 'student')
        await _create_user_with_role(session, 'admin7@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000006', 'student.six@example.com', status='pending')
        await session.commit()

    student_login = await client.post('/auth/login', json={'email': 'student2@example.com', 'password': 'StrongPass123'})
    student_token = student_login.json()['data']['access_token']
    approve_forbidden = await client.post(f'/api/v1/admin/registrations/{registration.id}/approve', headers={'Authorization': f'Bearer {student_token}'})
    reject_forbidden = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {student_token}'},
        json={'reason': 'Not authorized'},
    )
    assert approve_forbidden.status_code == 403
    assert reject_forbidden.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_user_cannot_approve_or_reject(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin8@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000007', 'student.seven@example.com', status='pending')
        await session.commit()

    unauthenticated_approve = await client.post(f'/api/v1/admin/registrations/{registration.id}/approve')
    unauthenticated_reject = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        json={'reason': 'No auth'},
    )
    assert unauthenticated_approve.status_code == 401
    assert unauthenticated_reject.status_code == 401


@pytest.mark.asyncio
async def test_cannot_reject_approved_registration(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin9@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000008', 'student.eight@example.com', status='approved')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin9@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(
        f'/api/v1/admin/registrations/{registration.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'reason': 'Too late'},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cannot_approve_rejected_registration(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'admin10@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000009', 'student.nine@example.com', status='rejected')
        await session.commit()

    admin_login = await client.post('/auth/login', json={'email': 'admin10@example.com', 'password': 'StrongPass123'})
    admin_token = admin_login.json()['data']['access_token']
    response = await client.post(f'/api/v1/admin/registrations/{registration.id}/approve', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 400


async def _get_admin_token(client, email: str) -> str:
    response = await client.post('/auth/login', json={'email': email, 'password': 'StrongPass123'})
    return response.json()['data']['access_token']


@pytest.mark.asyncio
async def test_admin_can_update_one_and_multiple_editable_fields_and_values_persist(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2-admin@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000010', 'stage2.student@example.com')
        await session.commit()

    token = await _get_admin_token(client, 'stage2-admin@example.com')
    response = await client.patch(
        f'/api/v1/admin/registrations/{registration.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'first_name': 'meera', 'department': 'Data Science and Data Analysis', 'academic_year': 'Second Year', 'roll_number': 'fcs26099', 'notes': 'Corrected by admin'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['first_name'] == 'Meera'
    assert data['department'] == 'Data Science and Data Analysis'
    assert data['academic_year'] == 'Second Year'
    assert data['roll_number'] == 'FCS26099'
    assert data['notes'] == 'Corrected by admin'

    detail = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {token}'})
    assert detail.status_code == 200
    assert detail.json()['roll_number'] == 'FCS26099'
    assert detail.json()['email'] == 'stage2.student@example.com'


@pytest.mark.asyncio
async def test_non_admin_and_unauthenticated_users_cannot_update_registration(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2-student@example.com', 'StrongPass123', 'student')
        await _create_user_with_role(session, 'stage2-admin-two@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000011', 'stage2.student2@example.com')
        await session.commit()

    student_token = await _get_admin_token(client, 'stage2-student@example.com')
    forbidden = await client.patch(
        f'/api/v1/admin/registrations/{registration.id}',
        headers={'Authorization': f'Bearer {student_token}'},
        json={'first_name': 'Blocked'},
    )
    unauthenticated = await client.patch(f'/api/v1/admin/registrations/{registration.id}', json={'first_name': 'Blocked'})
    assert forbidden.status_code == 403
    assert unauthenticated.status_code == 401


@pytest.mark.asyncio
async def test_invalid_department_and_academic_year_are_rejected(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2-validation@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000012', 'stage2.student3@example.com')
        await session.commit()

    token = await _get_admin_token(client, 'stage2-validation@example.com')
    invalid_department = await client.patch(
        f'/api/v1/admin/registrations/{registration.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'department': 'Invalid Department'},
    )
    invalid_year = await client.patch(
        f'/api/v1/admin/registrations/{registration.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'academic_year': 'Fourth Year'},
    )
    assert invalid_department.status_code == 422
    assert invalid_department.json()['detail'] == 'Department is invalid'
    assert invalid_year.status_code == 422
    assert invalid_year.json()['detail'] == 'Academic year is invalid'


@pytest.mark.asyncio
async def test_system_fields_cannot_be_changed(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2-protected@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000013', 'stage2.student4@example.com')
        await session.commit()

    token = await _get_admin_token(client, 'stage2-protected@example.com')
    for field, value in {
        'registration_number': 'PG26-999999',
        'status': 'approved',
        'payment_status': 'verified',
        'payment_proof': 'changed-proof',
        'approved_at': '2026-08-19T00:00:00Z',
        'checked_in': True,
    }.items():
        response = await client.patch(
            f'/api/v1/admin/registrations/{registration.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={field: value},
        )
        assert response.status_code == 422, field

    detail = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {token}'})
    assert detail.json()['registration_number'] == 'PG26-000013'
    assert detail.json()['status'] == 'pending'


@pytest.mark.asyncio
async def test_editing_does_not_change_pass_qr_email_or_registration_state(client, email_service_override):
    async with get_session() as session:
        admin = await _create_user_with_role(session, 'stage2-side-effects@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000014', 'stage2.student5@example.com', status='approved')
        registration.approved_by = admin.id
        registration.approved_at = datetime.now(timezone.utc)
        registration.checked_in = True
        registration.checked_in_at = datetime.now(timezone.utc)
        await session.flush()
        pass_obj, qr = await _create_pass_and_qr(session, registration)
        await session.commit()
        original = (registration.registration_number, registration.status, registration.approved_by, registration.approved_at, registration.checked_in, registration.checked_in_at, pass_obj.id, qr.id, qr.qr_token)

    token = await _get_admin_token(client, 'stage2-side-effects@example.com')
    response = await client.patch(
        f'/api/v1/admin/registrations/{registration.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'email': 'changed.student@example.com', 'phone': '9123456789'},
    )
    assert response.status_code == 200
    assert email_service_override.calls == []

    async with get_session() as session:
        updated = (await session.execute(select(Registration).where(Registration.id == registration.id))).scalars().one()
        passes = (await session.execute(select(Pass).where(Pass.registration_id == registration.id))).scalars().all()
        qrcodes = (await session.execute(select(QRCode).where(QRCode.pass_id == pass_obj.id))).scalars().all()
        assert updated.registration_number == original[0]
        assert updated.status == original[1]
        assert updated.approved_by == original[2]
        assert updated.approved_at == original[3].replace(tzinfo=None)
        assert updated.checked_in == original[4]
        assert updated.checked_in_at == original[5].replace(tzinfo=None)
        assert len(passes) == 1 and passes[0].id == original[6]
        assert len(qrcodes) == 1 and qrcodes[0].id == original[7] and qrcodes[0].qr_token == original[8]


@pytest.mark.asyncio
async def test_admin_can_fix_only_known_malformed_roll_number(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2c2-admin@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000015', 'stage2c2.student@example.com')
        registration.roll_number = 'FAI2401'
        await session.commit()

    token = await _get_admin_token(client, 'stage2c2-admin@example.com')
    response = await client.patch(f'/api/v1/admin/registrations/{registration.id}/fix-roll-number', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['roll_number'] == 'FAI24001'

    detail = await client.get(f'/api/v1/admin/registrations/{registration.id}', headers={'Authorization': f'Bearer {token}'})
    assert detail.json()['registration_number'] == 'PG26-000015'
    assert detail.json()['roll_number'] == 'FAI24001'


@pytest.mark.asyncio
async def test_roll_fix_leaves_correct_values_and_rejects_unsafe_values(client):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2c2-safe@example.com', 'StrongPass123', 'admin')
        correct = await _create_registration(session, 'PG26-000016', 'stage2c2.correct@example.com')
        correct.roll_number = 'FAI24001'
        unsafe = await _create_registration(session, 'PG26-000017', 'stage2c2.unsafe@example.com')
        unsafe.roll_number = 'FAI24RATETEST'
        await session.commit()

    token = await _get_admin_token(client, 'stage2c2-safe@example.com')
    unchanged = await client.patch(f'/api/v1/admin/registrations/{correct.id}/fix-roll-number', headers={'Authorization': f'Bearer {token}'})
    rejected = await client.patch(f'/api/v1/admin/registrations/{unsafe.id}/fix-roll-number', headers={'Authorization': f'Bearer {token}'})
    assert unchanged.status_code == 200
    assert unchanged.json()['changed'] is False
    assert unchanged.json()['message'] == 'Roll number is already in the correct format.'
    assert rejected.status_code == 422
    assert rejected.json()['detail'] == 'Roll number cannot be automatically corrected. Please use Edit.'


@pytest.mark.asyncio
async def test_roll_fix_requires_admin_and_preserves_pass_qr_state(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2c2-student@example.com', 'StrongPass123', 'student')
        admin = await _create_user_with_role(session, 'stage2c2-side-effects@example.com', 'StrongPass123', 'admin')
        registration = await _create_registration(session, 'PG26-000018', 'stage2c2.sideeffects@example.com', status='approved')
        registration.roll_number = 'FAI2412'
        registration.approved_by = admin.id
        registration.checked_in = True
        pass_obj, qr = await _create_pass_and_qr(session, registration)
        await session.commit()

    student_token = await _get_admin_token(client, 'stage2c2-student@example.com')
    forbidden = await client.patch(f'/api/v1/admin/registrations/{registration.id}/fix-roll-number', headers={'Authorization': f'Bearer {student_token}'})
    assert forbidden.status_code == 403

    admin_token = await _get_admin_token(client, 'stage2c2-side-effects@example.com')
    response = await client.patch(f'/api/v1/admin/registrations/{registration.id}/fix-roll-number', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json()['roll_number'] == 'FAI24012'
    assert email_service_override.calls == []

    async with get_session() as session:
        updated = (await session.execute(select(Registration).where(Registration.id == registration.id))).scalars().one()
        passes = (await session.execute(select(Pass).where(Pass.registration_id == registration.id))).scalars().all()
        qrcodes = (await session.execute(select(QRCode).where(QRCode.pass_id == pass_obj.id))).scalars().all()
        assert updated.registration_number == 'PG26-000018'
        assert updated.status == 'approved'
        assert updated.checked_in is True
        assert len(passes) == 1 and passes[0].id == pass_obj.id
        assert len(qrcodes) == 1 and qrcodes[0].id == qr.id


@pytest.mark.asyncio
async def test_admin_email_actions_reuse_canonical_templates_and_existing_pass(client, email_service_override):
    async with get_session() as session:
        await _create_user_with_role(session, 'stage2c3-admin@example.com', 'StrongPass123', 'admin')
        pending = await _create_registration(session, 'PG26-000019', 'stage2c3.pending@example.com')
        approved = await _create_registration(session, 'PG26-000020', 'stage2c3.approved@example.com', status='approved')
        pass_obj, qr = await _create_pass_and_qr(session, approved)
        await session.commit()

    token = await _get_admin_token(client, 'stage2c3-admin@example.com')
    confirmation = await client.post(f'/api/v1/admin/registrations/{pending.id}/resend-confirmation-email', headers={'Authorization': f'Bearer {token}'})
    assert confirmation.status_code == 200
    confirmation_subject, confirmation_body = build_registration_confirmation_email(pending.registration_number)
    assert email_service_override.calls[-1]['subject'] == confirmation_subject
    assert email_service_override.calls[-1]['body'] == confirmation_body

    sent = await client.post(f'/api/v1/admin/registrations/{approved.id}/send-pass-email', headers={'Authorization': f'Bearer {token}'})
    assert sent.status_code == 200
    pass_subject, pass_body = build_registration_approval_email(approved.registration_number, pass_obj.pass_number)
    assert email_service_override.calls[-1]['subject'] == pass_subject
    assert email_service_override.calls[-1]['body'] == pass_body
    assert email_service_override.calls[-1]['attachments'][0][0] == 'Pragyarambh_Pass.png'
    assert email_service_override.calls[-1]['attachments'][0][1]
    assert sent.json()['pass_number'] == pass_obj.pass_number
    assert (await client.get(f'/api/v1/admin/registrations/{approved.id}/pass', headers={'Authorization': f'Bearer {token}'})).json()['qr']['qr_token'] == qr.qr_token


@pytest.mark.asyncio
async def test_public_registration_status_is_privacy_safe_and_reuses_email_actions(client, email_service_override):
    from api.registration import status_limiter
    status_limiter.requests.clear()
    async with get_session() as session:
        pending = await _create_registration(session, 'PG26-000021', 'stage2d.pending@example.com')
        approved = await _create_registration(session, 'PG26-000022', 'stage2d.approved@example.com', status='approved')
        pass_obj, _qr = await _create_pass_and_qr(session, approved)
        rejected = await _create_registration(session, 'PG26-000023', 'stage2d.rejected@example.com', status='rejected')
        rejected.rejected_reason = 'Internal reason'
        await session.commit()

    pending_response = await client.post('/api/v1/registration/status', json={'email': pending.email})
    approved_response = await client.post('/api/v1/registration/status', json={'email': approved.email})
    rejected_response = await client.post('/api/v1/registration/status', json={'email': rejected.email})
    unknown_response = await client.post('/api/v1/registration/status', json={'email': 'unknown.stage2d@example.com'})
    assert pending_response.json()['status'] == 'pending'
    assert approved_response.json()['status'] == 'approved'
    assert rejected_response.json()['status'] == 'rejected'
    assert unknown_response.json()['found'] is False
    for response in (pending_response, approved_response, rejected_response, unknown_response):
        assert 'payment' not in response.text.lower()
        assert 'qr' not in response.text.lower()
        assert 'internal reason' not in response.text.lower()
        assert 'id' not in response.json()

    confirmation = await client.post('/api/v1/registration/status/resend-confirmation', json={'email': pending.email})
    assert confirmation.status_code == 200
    confirmation_subject, confirmation_body = build_registration_confirmation_email(pending.registration_number)
    assert email_service_override.calls[-1]['subject'] == confirmation_subject
    assert email_service_override.calls[-1]['body'] == confirmation_body

    pass_response = await client.post('/api/v1/registration/status/resend-pass', json={'email': approved.email})
    assert pass_response.status_code == 200
    pass_subject, pass_body = build_registration_approval_email(approved.registration_number, pass_obj.pass_number)
    assert email_service_override.calls[-1]['subject'] == pass_subject
    assert email_service_override.calls[-1]['body'] == pass_body
    assert email_service_override.calls[-1]['attachments'][0][0] == 'Pragyarambh_Pass.png'


@pytest.mark.asyncio
async def test_public_email_actions_handle_delivery_failure(client, email_service_override):
    from api.registration import status_limiter
    status_limiter.requests.clear()
    async with get_session() as session:
        registration = await _create_registration(session, 'PG26-000024', 'stage2d.failure@example.com')
        await session.commit()

    email_service_override.should_fail = True
    response = await client.post('/api/v1/registration/status/resend-confirmation', json={'email': registration.email})
    assert response.status_code == 200
    assert response.json()['email_sent'] is False
    assert 'could not be delivered' in response.json()['message'].lower()
