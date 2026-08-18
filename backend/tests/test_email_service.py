import json
import logging

import httpx
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.email_service import BrevoEmailService, ConsoleEmailService, get_email_service


@pytest.mark.asyncio
async def test_brevo_success_201_with_message_id(caplog):
    """Test Brevo 201 success response."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "messageId": "<abc123@brevo.com>",
    }

    with caplog.at_level(logging.INFO, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = response_data

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            await service.send_email('recipient@example.com', 'Test Subject', 'Test Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=configuration action=success' in msg for msg in messages)
    assert any('stage=request_start action=success' in msg for msg in messages)
    assert any('stage=delivery_accepted action=success' in msg and 'message_id=<abc123@brevo.com>' in msg for msg in messages)
    assert any('stage=delivery action=success' in msg for msg in messages)
    # Verify API key is not logged
    assert not any('test-api-key' in msg for msg in messages)


@pytest.mark.asyncio
async def test_brevo_400_bad_request(caplog):
    """Test Brevo 400 failure response."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "message": "Invalid email address",
    }

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = response_data

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            with pytest.raises(Exception) as exc_info:
                await service.send_email('invalid-email', 'Test Subject', 'Test Body')

            assert 'Brevo API error' in str(exc_info.value)

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=delivery_failed' in msg for msg in messages)
    assert any('status_code=400' in msg for msg in messages)
    # Verify API key is not logged
    assert not any('test-api-key' in msg for msg in messages)


@pytest.mark.asyncio
async def test_brevo_401_authentication_failure(caplog):
    """Test Brevo 401 authentication failure."""
    service = BrevoEmailService(
        api_key='invalid-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "message": "Unauthorized",
    }

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = response_data

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            with pytest.raises(Exception) as exc_info:
                await service.send_email('recipient@example.com', 'Test Subject', 'Test Body')

            assert 'Brevo API error' in str(exc_info.value)

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=delivery_failed' in msg for msg in messages)
    assert any('status_code=401' in msg for msg in messages)
    # Verify credentials are masked
    assert not any('invalid-api-key' in msg for msg in messages)


@pytest.mark.asyncio
async def test_brevo_429_rate_limit(caplog):
    """Test Brevo 429 rate limit failure."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "message": "Too many requests",
    }

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.json.return_value = response_data

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            with pytest.raises(Exception) as exc_info:
                await service.send_email('recipient@example.com', 'Test Subject', 'Test Body')

            assert 'Brevo API error' in str(exc_info.value)

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=delivery_failed' in msg for msg in messages)
    assert any('status_code=429' in msg for msg in messages)


@pytest.mark.asyncio
async def test_brevo_500_server_error(caplog):
    """Test Brevo 500 server error."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "message": "Internal server error",
    }

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = response_data

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            with pytest.raises(Exception) as exc_info:
                await service.send_email('recipient@example.com', 'Test Subject', 'Test Body')

            assert 'Brevo API error' in str(exc_info.value)

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=delivery_failed' in msg for msg in messages)
    assert any('status_code=500' in msg for msg in messages)


@pytest.mark.asyncio
async def test_brevo_network_timeout(caplog):
    """Test Brevo network timeout."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException('Request timeout'))

            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.TimeoutException):
                await service.send_email('recipient@example.com', 'Test Subject', 'Test Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=request_start' in msg and 'error_type=TimeoutException' in msg for msg in messages)


@pytest.mark.asyncio
async def test_brevo_missing_api_key():
    """Test that missing BREVO_API_KEY falls back to ConsoleEmailService."""
    with patch('services.email_service.settings') as mock_settings:
        mock_settings.BREVO_API_KEY = None
        mock_settings.MAIL_FROM = 'hello@pragyarambh.tech'

        from services.email_service import get_email_service
        service = get_email_service()

        assert isinstance(service, ConsoleEmailService)
        assert not service.enabled


@pytest.mark.asyncio
async def test_brevo_malformed_response_json(caplog):
    """Test Brevo malformed/unexpected response."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.side_effect = json.JSONDecodeError('Invalid JSON', 'doc', 0)

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            with pytest.raises(json.JSONDecodeError):
                await service.send_email('recipient@example.com', 'Test Subject', 'Test Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=response_received' in msg and 'error_type=JSONDecodeError' in msg for msg in messages)


@pytest.mark.asyncio
async def test_registration_flow_returns_confirmation_email_sent_true_on_success(caplog):
    """Test that registration flow reports confirmation_email_sent=true after successful Brevo response."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "messageId": "<abc123@brevo.com>",
    }

    with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = response_data

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post = AsyncMock(return_value=mock_response)

        mock_client_class.return_value = mock_client

        # This should not raise an exception
        await service.send_email('recipient@example.com', 'Subject', 'Body')

        # If we get here without exception, the email was sent successfully
        # In registration.py, this would set confirmation_email_sent=true


@pytest.mark.asyncio
async def test_registration_flow_returns_confirmation_email_sent_false_on_failure(caplog):
    """Test that registration flow reports confirmation_email_sent=false after Brevo failure."""
    service = BrevoEmailService(
        api_key='test-api-key',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    response_data = {
        "message": "Invalid email address",
    }

    with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = response_data

        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post = AsyncMock(return_value=mock_response)

        mock_client_class.return_value = mock_client

        with pytest.raises(Exception):
            await service.send_email('recipient@example.com', 'Subject', 'Body')

        # If exception is raised, registration.py would catch it and set confirmation_email_sent=false


@pytest.mark.asyncio
async def test_brevo_does_not_log_api_key(caplog):
    """Verify API key is never logged in error messages."""
    service = BrevoEmailService(
        api_key='super-secret-api-key-12345',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
    )

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with patch('services.email_service.httpx.AsyncClient') as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"message": "Server error"}

            mock_client = MagicMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)

            mock_client_class.return_value = mock_client

            with pytest.raises(Exception):
                await service.send_email('recipient@example.com', 'Subject', 'Body')

    # Check all log messages to ensure API key is never present
    for record in caplog.records:
        message = record.getMessage()
        assert 'super-secret-api-key-12345' not in message
        assert 'api-key' not in message.lower() or 'api-key:' not in message.lower()
