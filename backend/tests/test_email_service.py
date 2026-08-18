import logging
import smtplib

import pytest

from services.email_service import SMTPEmailService


class AuthenticationFailingSMTP:
    def __init__(self, *args, **kwargs):
        self.quit_called = False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        return None

    def login(self, username, password):
        raise smtplib.SMTPAuthenticationError(535, b'authentication failed for secret-password')

    def quit(self):
        self.quit_called = True


class SuccessfulSMTP:
    def __init__(self, *args, **kwargs):
        self.sent = False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        return None

    def login(self, username, password):
        return None

    def send_message(self, message):
        self.sent = True

    def quit(self):
        return None


class ConnectionFailingSMTP:
    def __init__(self, *args, **kwargs):
        raise TimeoutError('timed out while connecting to smtp.titan.email')


class StartTLSFailingSMTP:
    def __init__(self, *args, **kwargs):
        self.quit_called = False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        raise TimeoutError('timed out during STARTTLS handshake')

    def quit(self):
        self.quit_called = True


class SendmailFailingSMTP:
    def __init__(self, *args, **kwargs):
        self.quit_called = False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        return None

    def login(self, username, password):
        return None

    def send_message(self, message):
        raise smtplib.SMTPRecipientsRefused({'recipient@example.com': (550, 'mailbox unavailable')})

    def quit(self):
        self.quit_called = True


@pytest.mark.asyncio
async def test_smtp_diagnostics_mask_credentials_and_reraise(monkeypatch, caplog):
    monkeypatch.setattr(smtplib, 'SMTP_SSL', AuthenticationFailingSMTP)
    service = SMTPEmailService(
        host='smtp.titan.email',
        port=465,
        username='hello@pragyarambh.tech',
        password='secret-password',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
        use_tls=False,
    )

    with caplog.at_level(logging.ERROR, logger='services.email_service'):
        with pytest.raises(smtplib.SMTPAuthenticationError):
            await service.send_email('recipient@example.com', 'Subject', 'Body')

    diagnostic = next(record.getMessage() for record in caplog.records if 'SMTP diagnostic:' in record.getMessage())
    assert 'stage=authentication' in diagnostic
    assert 'host=smtp.titan.email' in diagnostic
    assert 'port=465' in diagnostic
    assert 'he***@pragyarambh.tech' in diagnostic
    assert 'secret-password' not in diagnostic
    assert 'hello@pragyarambh.tech' not in diagnostic


@pytest.mark.asyncio
async def test_smtp_diagnostics_log_connection_failure_with_stage_and_action(monkeypatch, caplog):
    monkeypatch.setattr(smtplib, 'SMTP', ConnectionFailingSMTP)
    service = SMTPEmailService(
        host='smtp.titan.email',
        port=587,
        username='hello@pragyarambh.tech',
        password='secret-password',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
        use_tls=True,
    )

    with caplog.at_level(logging.INFO, logger='services.email_service'):
        with pytest.raises(TimeoutError):
            await service.send_email('recipient@example.com', 'Subject', 'Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=configuration action=start' in message for message in messages)
    assert any('stage=connection action=start' in message for message in messages)
    assert any('stage=connection' in message and 'error_type=TimeoutError' in message for message in messages)
    assert any('timed out while connecting to smtp.titan.email' in message for message in messages)


@pytest.mark.asyncio
async def test_smtp_diagnostics_log_starttls_failure_with_stage_and_action(monkeypatch, caplog):
    monkeypatch.setattr(smtplib, 'SMTP', lambda *args, **kwargs: StartTLSFailingSMTP(*args, **kwargs))
    service = SMTPEmailService(
        host='smtp.titan.email',
        port=587,
        username='hello@pragyarambh.tech',
        password='secret-password',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
        use_tls=True,
    )

    with caplog.at_level(logging.INFO, logger='services.email_service'):
        with pytest.raises(TimeoutError):
            await service.send_email('recipient@example.com', 'Subject', 'Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=starttls action=start' in message for message in messages)
    assert any('stage=starttls' in message and 'error_type=TimeoutError' in message for message in messages)
    assert any('timed out during STARTTLS handshake' in message for message in messages)


@pytest.mark.asyncio
async def test_smtp_diagnostics_log_authentication_failure_with_stage_and_action(monkeypatch, caplog):
    monkeypatch.setattr(smtplib, 'SMTP', lambda *args, **kwargs: AuthenticationFailingSMTP())
    service = SMTPEmailService(
        host='smtp.titan.email',
        port=587,
        username='hello@pragyarambh.tech',
        password='secret-password',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
        use_tls=True,
    )

    with caplog.at_level(logging.INFO, logger='services.email_service'):
        with pytest.raises(smtplib.SMTPAuthenticationError):
            await service.send_email('recipient@example.com', 'Subject', 'Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=authentication action=start' in message for message in messages)
    assert any('stage=authentication' in message and 'error_type=SMTPAuthenticationError' in message for message in messages)


@pytest.mark.asyncio
async def test_smtp_diagnostics_log_sendmail_failure_with_stage_and_action(monkeypatch, caplog):
    monkeypatch.setattr(smtplib, 'SMTP', lambda *args, **kwargs: SendmailFailingSMTP())
    service = SMTPEmailService(
        host='smtp.titan.email',
        port=587,
        username='hello@pragyarambh.tech',
        password='secret-password',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
        use_tls=True,
    )

    with caplog.at_level(logging.INFO, logger='services.email_service'):
        with pytest.raises(smtplib.SMTPRecipientsRefused):
            await service.send_email('recipient@example.com', 'Subject', 'Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=sendmail action=start' in message for message in messages)
    assert any('stage=sendmail' in message and 'error_type=SMTPRecipientsRefused' in message for message in messages)


@pytest.mark.asyncio
async def test_smtp_diagnostics_log_success_without_password(monkeypatch, caplog):
    monkeypatch.setattr(smtplib, 'SMTP_SSL', SuccessfulSMTP)
    service = SMTPEmailService(
        host='smtp.titan.email',
        port=465,
        username='hello@pragyarambh.tech',
        password='secret-password',
        from_email='hello@pragyarambh.tech',
        from_name='Pragyarambh 3.0',
        use_tls=False,
    )

    with caplog.at_level(logging.INFO, logger='services.email_service'):
        await service.send_email('recipient@example.com', 'Subject', 'Body')

    messages = [record.getMessage() for record in caplog.records]
    assert any('stage=configuration action=success' in message and 'tls_mode=implicit_ssl' in message for message in messages)
    assert any('stage=connection action=success' in message for message in messages)
    assert any('stage=authentication action=success' in message for message in messages)
    assert any('stage=sendmail action=success' in message for message in messages)
    assert any('stage=delivery action=success' in message for message in messages)
    assert not any('secret-password' in message for message in messages)
