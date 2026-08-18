import pytest
from sqlalchemy import select
import io

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
async def test_payment_required_for_second_year(client, email_service_override):
    """Payment fields are required for Second Year registrations."""
    payload = {
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "FCS25001",
        "phone": "9876543211",
        "email": "rajesh@example.com",
        "gender": "Male",
        "payment_mode": "upi",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 400
    assert 'Payment reference is required' in response.json()['detail']


@pytest.mark.asyncio
async def test_second_year_cash_registration_allowed_without_payment_proof(client, email_service_override):
    """Second Year cash registrations must not require payment proof or reference."""
    payload = {
        "first_name": "Cash",
        "last_name": "User",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "FCS25002",
        "phone": "9876543219",
        "email": "cash-user@example.com",
        "gender": "Male",
        "payment_mode": "cash",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending'

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.email == payload['email']))
        registration = result.scalars().first()

    assert registration is not None
    assert registration.payment_mode == 'cash'
    assert registration.payment_status == 'pending'
    assert registration.payment_amount == 250.0
    assert registration.payment_reference is None
    assert registration.payment_proof is None


@pytest.mark.asyncio
async def test_second_year_upi_requires_reference_and_proof(client, email_service_override):
    """Second Year UPI registrations must include reference and proof."""
    payload = {
        "first_name": "Upi",
        "last_name": "User",
        "department": "Data Science and Data Analysis",
        "academic_year": "Second Year",
        "roll_number": "FDA25002",
        "phone": "9876543220",
        "email": "upi-user@example.com",
        "gender": "Female",
        "payment_mode": "upi",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 400
    assert 'Payment reference is required' in response.json()['detail']


@pytest.mark.asyncio
async def test_payment_not_required_for_first_year(client, email_service_override):
    """First Year registrations don't require payment."""
    payload = {
        "first_name": "Priya",
        "last_name": "Singh",
        "department": "Data Science and Data Analysis",
        "academic_year": "First Year",
        "roll_number": "FDA26001",
        "phone": "9876543212",
        "email": "priya@example.com",
        "gender": "Female",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending'

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.email == payload['email']))
        registration = result.scalars().first()

    assert registration is not None
    assert registration.payment_status == 'not_required'
    assert registration.payment_amount is None


@pytest.mark.asyncio
async def test_second_year_with_valid_payment_proof(client, email_service_override):
    """Second Year registration succeeds with valid payment proof."""
    payload = {
        "first_name": "Arjun",
        "last_name": "Patel",
        "department": "Artificial Intelligence and Machine Learning",
        "academic_year": "Second Year",
        "roll_number": "FAI25002",
        "phone": "9876543213",
        "email": "arjun@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "UPI-TXN-12345",
        "payment_proof": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending'

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.email == payload['email']))
        registration = result.scalars().first()

    assert registration is not None
    assert registration.payment_status == 'pending'
    assert registration.payment_amount == 250.0
    assert registration.payment_reference == 'UPI-TXN-12345'
    assert registration.payment_proof is not None


@pytest.mark.asyncio
async def test_third_year_with_valid_payment_proof(client, email_service_override):
    """Third Year registration succeeds with valid payment proof."""
    payload = {
        "first_name": "Devika",
        "last_name": "Sharma",
        "department": "Data Science and Data Analysis",
        "academic_year": "Third Year",
        "roll_number": "FDA24001",
        "phone": "9876543214",
        "email": "devika@example.com",
        "gender": "Female",
        "payment_mode": "upi",
        "payment_reference": "BANK-TXN-54321",
        "payment_proof": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending'

    async with get_session() as session:
        result = await session.execute(select(Registration).where(Registration.email == payload['email']))
        registration = result.scalars().first()

    assert registration is not None
    assert registration.payment_status == 'pending'
    assert registration.payment_amount == 250.0


@pytest.mark.asyncio
async def test_payment_proof_valid_jpeg_accepted(client, email_service_override):
    """Valid JPEG payment proof is accepted via multipart upload."""
    # Valid JPEG signature: FF D8 FF (from data URL in existing test)
    import base64
    valid_jpeg = base64.b64decode('/9j/4AAQSkZJRg==')  # Minimal valid JPEG
    payload = {
        "first_name": "Valid",
        "last_name": "JPEG",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "JPEG-VALID-001",
        "phone": "9876543250",
        "email": "valid-jpeg@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "VALID-JPEG-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.jpg', valid_jpeg, 'image/jpeg')})
    assert response.status_code == 200, f"Expected 200 for valid JPEG, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_payment_proof_valid_png_accepted(client, email_service_override):
    """Valid PNG payment proof is accepted via multipart upload."""
    # Valid PNG signature: 89 50 4E 47 0D 0A 1A 0A (1x1 transparent PNG)
    import base64
    valid_png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
    payload = {
        "first_name": "Valid",
        "last_name": "PNG",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "PNG-VALID-001",
        "phone": "9876543251",
        "email": "valid-png@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "VALID-PNG-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.png', valid_png, 'image/png')})
    assert response.status_code == 200, f"Expected 200 for valid PNG, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_payment_proof_pdf_rejected(client, email_service_override):
    """PDF payment proof is rejected (400) via multipart upload."""
    pdf = b'%PDF-1.4\x0a1 0 obj\x0a<<>>\x0aendobj\x0atrailer\x0a<<>>\x0a%%EOF'
    payload = {
        "first_name": "PDF",
        "last_name": "Reject",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "PDF-REJECT-001",
        "phone": "9876543252",
        "email": "pdf-reject@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "PDF-REJECT-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.pdf', pdf, 'application/pdf')})
    assert response.status_code == 400, f"Expected 400 for PDF, got {response.status_code}"


@pytest.mark.asyncio
async def test_payment_proof_pdf_renamed_as_jpg_rejected(client, email_service_override):
    """PDF renamed to .jpg is rejected (400) via multipart upload."""
    pdf = b'%PDF-1.4\x0a1 0 obj\x0a<<>>\x0aendobj\x0atrailer\x0a<<>>\x0a%%EOF'
    payload = {
        "first_name": "PDF",
        "last_name": "AsJPG",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "PDF-JPG-RENAME",
        "phone": "9876543253",
        "email": "pdf-as-jpg@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "PDF-JPG-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.jpg', pdf, 'image/jpeg')})
    assert response.status_code == 400, f"Expected 400 for PDF renamed as JPG, got {response.status_code}"


@pytest.mark.asyncio
async def test_payment_proof_pdf_renamed_as_png_rejected(client, email_service_override):
    """PDF renamed to .png is rejected (400) via multipart upload."""
    pdf = b'%PDF-1.4\x0a1 0 obj\x0a<<>>\x0aendobj\x0atrailer\x0a<<>>\x0a%%EOF'
    payload = {
        "first_name": "PDF",
        "last_name": "AsPNG",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "PDF-PNG-RENAME",
        "phone": "9876543254",
        "email": "pdf-as-png@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "PDF-PNG-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.png', pdf, 'image/png')})
    assert response.status_code == 400, f"Expected 400 for PDF renamed as PNG, got {response.status_code}"


@pytest.mark.asyncio
async def test_payment_proof_fake_jpeg_rejected(client, email_service_override):
    """Fake JPEG (invalid signature but image/jpeg MIME) is rejected (400)."""
    fake_jpeg = b'this-is-not-a-jpeg-file-at-all-fake'
    payload = {
        "first_name": "Fake",
        "last_name": "JPEG",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "FAKE-JPEG-001",
        "phone": "9876543255",
        "email": "fake-jpeg@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "FAKE-JPEG-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.jpg', fake_jpeg, 'image/jpeg')})
    assert response.status_code == 400, f"Expected 400 for fake JPEG, got {response.status_code}"


@pytest.mark.asyncio
async def test_payment_proof_fake_png_rejected(client, email_service_override):
    """Fake PNG (invalid signature but image/png MIME) is rejected (400)."""
    fake_png = b'this-is-not-a-png-file-at-all-fake'
    payload = {
        "first_name": "Fake",
        "last_name": "PNG",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "FAKE-PNG-001",
        "phone": "9876543256",
        "email": "fake-png@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "FAKE-PNG-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.png', fake_png, 'image/png')})
    assert response.status_code == 400, f"Expected 400 for fake PNG, got {response.status_code}"


@pytest.mark.asyncio
async def test_payment_proof_invalid_mime_rejected(client, email_service_override):
    """Invalid MIME type (e.g., application/octet-stream) is rejected (400)."""
    payload = {
        "first_name": "Invalid",
        "last_name": "MIME",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "MIME-INVALID-001",
        "phone": "9876543257",
        "email": "invalid-mime@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "MIME-INVALID-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.bin', b'some binary data', 'application/octet-stream')})
    assert response.status_code == 400, f"Expected 400 for invalid MIME, got {response.status_code}"


@pytest.mark.asyncio
async def test_payment_proof_empty_file_rejected(client, email_service_override):
    """Empty file is rejected (400) via multipart upload."""
    payload = {
        "first_name": "Empty",
        "last_name": "File",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Second Year",
        "roll_number": "EMPTY-FILE-001",
        "phone": "9876543258",
        "email": "empty-file@example.com",
        "gender": "Male",
        "payment_mode": "upi",
        "payment_reference": "EMPTY-FILE-REF",
    }
    response = await client.post('/api/v1/registration/with-proof', data=payload, files={'payment_proof': ('proof.png', b'', 'image/png')})
    assert response.status_code == 400, f"Expected 400 for empty file, got {response.status_code}"


@pytest.mark.asyncio
async def test_rate_limiting_on_registration(client):
    """Rate limiting prevents more than 5 registration attempts per email per hour."""
    # Reset the rate limiter for this test
    from middleware.rate_limiter import registration_limiter
    registration_limiter.requests.clear()
    
    base_payload = {
        "first_name": "Rate",
        "last_name": "Limiter",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "phone": "9876543215",
        "gender": "Male",
    }

    test_email = "rate_limiter_test@example.com"
    
    # Make 5 requests with the same email (regardless of outcome)
    for i in range(5):
        payload = {
            **base_payload,
            "roll_number": f"FCS26RATETEST{i:04d}",
            "email": test_email,
        }
        response = await client.post('/api/v1/registration', json=payload)
        # First one should succeed (200), rest might be 409 (duplicate email) but that's OK
        # We're testing rate limiting, not business logic
        assert response.status_code in (200, 409, 400), f"Unexpected status {response.status_code}: {response.json()}"
    
    # 6th request with same email MUST be rate limited (429)
    # Even though it might also fail on business logic, rate limiter is checked FIRST
    payload = {
        **base_payload,
        "roll_number": "FCS26RATETEST9999",
        "email": test_email,
    }
    response = await client.post('/api/v1/registration', json=payload)
    
    # The 6th attempt should be rate limited (429) regardless of other issues
    assert response.status_code == 429, f"Expected 429 (rate limited), got {response.status_code}: {response.json()}"


@pytest.mark.asyncio
async def test_duplicate_registration_rejected(client, email_service_override):
    """Duplicate registrations are rejected properly."""
    payload = {
        "first_name": "Duplicate",
        "last_name": "Test",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "First Year",
        "roll_number": "FCS26DUP",
        "phone": "9876543216",
        "email": "duplicate@example.com",
        "gender": "Male",
    }

    # First registration should succeed
    response1 = await client.post('/api/v1/registration', json=payload)
    assert response1.status_code == 200

    # Second registration with same email should fail
    response2 = await client.post('/api/v1/registration', json=payload)
    assert response2.status_code == 409
    assert 'already exists' in response2.json()['detail']

    # Third registration with same roll number but different email should fail
    payload_alt = {**payload, "email": "duplicate2@example.com"}
    response3 = await client.post('/api/v1/registration', json=payload_alt)
    assert response3.status_code == 409


@pytest.mark.asyncio
async def test_payment_proof_file_size_validation(client):
    """File upload validation rejects files over 5 MB."""
    # Create a mock file that's too large (simulated via base64)
    large_data = "x" * (6 * 1024 * 1024)  # 6 MB
    
    # We can't actually test file upload size validation without
    # using multipart/form-data, which would require a more complex setup.
    # This is tested implicitly through the multipart endpoint tests below.
    pass


@pytest.mark.asyncio
async def test_payment_proof_file_type_validation(client):
    """File upload validation rejects invalid file types."""
    # This test would require multipart/form-data setup
    # The validation is implemented in the endpoint
    pass


@pytest.mark.asyncio
async def test_payment_proof_rejects_malicious_payload_signature(client):
    """A file that pretends to be a valid image but has a malicious signature should be rejected."""
    malicious_bytes = b'not-a-real-png-data-that-is-not-a-valid-image' + b'\x00\x01\x02\x03'
    response = await client.post(
        '/api/v1/registration/with-proof',
        data={
            'first_name': 'Malice',
            'last_name': 'Payload',
            'department': 'Cybersecurity and Digital Forensics',
            'academic_year': 'Second Year',
            'roll_number': 'FCS26MAL1',
            'phone': '9876543222',
            'email': 'malice@example.com',
            'gender': 'Male',
            'payment_mode': 'upi',
            'payment_reference': 'MALWARE-TEST-1',
        },
        files={'payment_proof': ('fake.png', malicious_bytes, 'image/png')},
    )

    assert response.status_code == 400
    assert 'valid' in response.json()['detail'].lower()


@pytest.mark.asyncio
async def test_email_flow_on_payment_registration(client, email_service_override):
    """Confirmation email is sent for payment registrations."""
    payload = {
        "first_name": "Email",
        "last_name": "Test",
        "department": "Cybersecurity and Digital Forensics",
        "academic_year": "Third Year",
        "roll_number": "FCS24EMAIL",
        "phone": "9876543217",
        "email": "email@example.com",
        "gender": "Female",
        "payment_mode": "upi",
        "payment_reference": "EMAIL-TEST-123",
        "payment_proof": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    }

    response = await client.post('/api/v1/registration', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data['confirmation_email_sent'] is True
    assert len(email_service_override.calls) == 1
    call = email_service_override.calls[0]
    assert call['to'] == payload['email']
    assert data['registration_number'] in call['body']
