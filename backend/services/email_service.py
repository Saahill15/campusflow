from abc import ABC, abstractmethod
import asyncio
import httpx
import json
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Brevo API endpoint
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_REQUEST_TIMEOUT = 30.0

EmailAttachment = tuple[str, bytes, str]


class EmailService(ABC):
    @property
    @abstractmethod
    def enabled(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str, attachments: list[EmailAttachment] | None = None) -> None:
        raise NotImplementedError()


class ConsoleEmailService(EmailService):
    @property
    def enabled(self) -> bool:
        return False

    async def send_email(self, to: str, subject: str, body: str, attachments: list[EmailAttachment] | None = None) -> None:
        # simple console implementation for dev/test; does not count as delivery
        logger.info("Email delivery disabled. Preview for %s: %s", to, subject)
        logger.info("Body:\n%s", body)
        if attachments:
            logger.info("Attachments: %s", [attachment[0] for attachment in attachments])


class BrevoEmailService(EmailService):
    @property
    def enabled(self) -> bool:
        return True

    def __init__(
        self,
        api_key: str,
        from_email: str,
        from_name: str | None,
    ) -> None:
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name

    @staticmethod
    def _mask_address(value: str | None) -> str:
        if not value:
            return 'not_configured'
        local, separator, domain = value.partition('@')
        if not separator:
            return '***'
        return f'{local[:2]}***@{domain}'

    def _safe_error_message(self, exc: Exception) -> str:
        message = str(exc)
        # Remove any accidentally logged credentials
        if self.api_key and self.api_key in message:
            message = message.replace(self.api_key, '***')
        if self.from_email:
            message = message.replace(self.from_email, self._mask_address(self.from_email))
        return message

    def _log_brevo_start(self, stage: str, **details: str) -> None:
        detail_string = ' '.join(f'{key}={value}' for key, value in details.items())
        logger.info(
            'Brevo diagnostic: stage=%s action=start from_address=%s %s',
            stage,
            self._mask_address(self.from_email),
            detail_string,
        )

    def _log_brevo_failure(self, stage: str, exc: Exception, **details: str) -> None:
        detail_string = ' '.join(f'{key}={value}' for key, value in details.items())
        logger.error(
            'Brevo diagnostic: stage=%s from_address=%s error_type=%s error_message=%s%s',
            stage,
            self._mask_address(self.from_email),
            type(exc).__name__,
            self._safe_error_message(exc),
            f' {detail_string}' if detail_string else '',
        )

    def _log_brevo_success(self, stage: str, **details: str) -> None:
        detail_string = ' '.join(f'{key}={value}' for key, value in details.items())
        logger.info(
            'Brevo diagnostic: stage=%s action=success from_address=%s %s',
            stage,
            self._mask_address(self.from_email),
            detail_string,
        )

    async def _send_message(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: list[EmailAttachment] | None = None,
    ) -> None:
        self._log_brevo_start('configuration', api_endpoint=BREVO_API_URL)
        try:
            self._log_brevo_success('configuration', api_endpoint=BREVO_API_URL)

            # Extract recipient name if available
            recipient_name = to.split('@')[0] if '@' in to else None

            # Build Brevo API request
            request_payload = {
                "sender": {
                    "name": self.from_name or "Pragyarambh 3.0",
                    "email": self.from_email,
                },
                "to": [
                    {
                        "email": to,
                        "name": recipient_name,
                    }
                ],
                "subject": subject,
                "htmlContent": body,
            }
            if attachments:
                import base64

                request_payload["attachment"] = [
                    {
                        "name": filename,
                        "content": base64.b64encode(content).decode('ascii'),
                    }
                    for filename, content, _content_type in attachments
                ]

            self._log_brevo_start('request_start', recipient_email=self._mask_address(to))
            try:
                async with httpx.AsyncClient(timeout=BREVO_REQUEST_TIMEOUT) as client:
                    response = await client.post(
                        BREVO_API_URL,
                        json=request_payload,
                        headers={
                            "api-key": self.api_key,
                            "Content-Type": "application/json",
                        },
                    )
            except Exception as exc:
                self._log_brevo_failure('request_start', exc)
                raise

            self._log_brevo_success('request_start', status_code=response.status_code)

            # Parse response
            self._log_brevo_start('response_received')
            try:
                response_data = response.json()
            except Exception as exc:
                self._log_brevo_failure('response_received', exc, status_code=response.status_code)
                raise

            self._log_brevo_success('response_received', status_code=response.status_code)

            # Check for success (HTTP 201 with messageId)
            if response.status_code == 201:
                message_id = response_data.get('messageId', 'unknown')
                self._log_brevo_start('delivery_accepted', message_id=message_id)
                try:
                    # Success - log and return
                    self._log_brevo_success('delivery_accepted', message_id=message_id)
                except Exception as exc:
                    self._log_brevo_failure('delivery_accepted', exc)
                    raise
            else:
                # Failure - extract error information
                error_message = response_data.get('message', f'HTTP {response.status_code}')
                self._log_brevo_start('delivery_failed', status_code=response.status_code, error=error_message)
                try:
                    raise Exception(f'Brevo API error: {error_message} (HTTP {response.status_code})')
                except Exception as exc:
                    self._log_brevo_failure('delivery_failed', exc, status_code=response.status_code)
                    raise

        except Exception:
            raise

    async def send_email(self, to: str, subject: str, body: str, attachments: list[EmailAttachment] | None = None) -> None:
        try:
            await self._send_message(to, subject, body, attachments=attachments)
        except Exception as exc:
            self._log_brevo_failure('delivery', exc)
            raise
        self._log_brevo_success('delivery')


def get_email_service() -> EmailService:
    if settings.BREVO_API_KEY and settings.MAIL_FROM:
        return BrevoEmailService(
            api_key=settings.BREVO_API_KEY,
            from_email=settings.MAIL_FROM,
            from_name=settings.MAIL_FROM_NAME,
        )
    return ConsoleEmailService()


def _registration_email_template(title: str, subtitle: str, detail_rows: list[tuple[str, str]], accent: str = '#CC9E4C') -> str:
    rows_html = ''.join(
        f"<tr><td style='padding: 10px 0; font-size: 13px; color: #d9c9ad; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700;'>{label}:</td><td style='padding: 10px 0; font-size: 15px; color: #f8f1e6; font-weight: 600;'>{value}</td></tr>"
        for label, value in detail_rows
    )
    return f"""
    <html>
      <body style="margin:0; padding:0; background:#120d0a; font-family:Arial, Helvetica, sans-serif; color:#f7f0e8;">
        <div style="max-width: 640px; margin: 32px auto; background: #1a120d; border: 1px solid rgba(204,158,76,0.35); border-radius: 18px; overflow: hidden;">
          <div style="background: linear-gradient(135deg, #1a120d 0%, #2b1d14 100%); padding: 28px 28px 18px; border-bottom: 1px solid rgba(204,158,76,0.28);">
            <div style="font-size: 11px; letter-spacing: 0.28em; font-weight: 800; color: {accent}; text-transform: uppercase;">Pragyarambh 3.0</div>
            <h1 style="margin: 16px 0 6px; font-size: 32px; line-height: 1.15; color: #f7f0e8;">{title}</h1>
            <p style="margin: 0; color: #d9c9ad; font-size: 15px; line-height: 1.6;">{subtitle}</p>
          </div>
          <div style="padding: 20px 28px 28px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width:100%; border-collapse: collapse;">
              {rows_html}
            </table>
          </div>
          <div style="padding: 0 28px 28px; color: #d9c9ad; font-size: 14px; line-height: 1.7;">
            <p style="margin: 0;">Thank you for being part of Pragyarambh 3.0.</p>
          </div>
        </div>
      </body>
    </html>
    """


def build_registration_confirmation_email(registration_number: str) -> tuple[str, str]:
    subject = "Pragyarambh 3.0 - Registration Submitted Successfully"
    body = _registration_email_template(
        title='Registration Submitted Successfully',
        subtitle='Your registration has been received and is currently awaiting review by the event team.',
        detail_rows=[
            ('Registration Number', registration_number),
            ('Status', 'Pending Approval'),
            ('Next Step', 'Your official pass will be sent once the registration is approved.'),
        ],
    )
    return subject, body


def build_registration_approval_email(registration_number: str, pass_number: str) -> tuple[str, str]:
    subject = "Pragyarambh 3.0 - Registration Approved"
    body = _registration_email_template(
        title='Registration Approved',
        subtitle='Congratulations! Your entry pass has been issued and is ready for use.',
        detail_rows=[
            ('Registration Number', registration_number),
            ('Pass Number', pass_number),
            ('Status', 'Approved'),
            ('Pass', 'Attached as a PNG image with this email.'),
        ],
    )
    return subject, body


def build_registration_rejection_email(registration_number: str, reason: str) -> tuple[str, str]:
    subject = "Pragyarambh 3.0 - Registration Review Result"
    body = _registration_email_template(
        title='Registration Rejected',
        subtitle='We regret to inform you that your registration was not approved.',
        detail_rows=[
            ('Registration Number', registration_number),
            ('Status', 'Rejected'),
            ('Reason', reason),
            ('Support', 'Contact the event administration team for assistance.'),
        ],
    )
    return subject, body
