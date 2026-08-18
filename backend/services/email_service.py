from abc import ABC, abstractmethod
import asyncio
from email.message import EmailMessage
import logging
import smtplib
import ssl

from core.config import settings

logger = logging.getLogger(__name__)


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


class SMTPEmailService(EmailService):
    @property
    def enabled(self) -> bool:
        return True
    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        from_email: str,
        from_name: str | None,
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.from_name = from_name
        self.use_tls = use_tls

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
        if self.password:
            message = message.replace(self.password, '***')
        if self.username:
            message = message.replace(self.username, self._mask_address(self.username))
        if self.from_email:
            message = message.replace(self.from_email, self._mask_address(self.from_email))
        return message

    def _log_smtp_start(self, stage: str, **details: str) -> None:
        detail_string = ' '.join(f'{key}={value}' for key, value in details.items())
        logger.info(
            'SMTP diagnostic: stage=%s action=start host=%s port=%s username=%s from_address=%s %s',
            stage,
            self.host,
            self.port,
            self._mask_address(self.username),
            self._mask_address(self.from_email),
            detail_string,
        )

    def _log_smtp_failure(self, stage: str, exc: Exception, **details: str) -> None:
        detail_string = ' '.join(f'{key}={value}' for key, value in details.items())
        logger.error(
            'SMTP diagnostic: stage=%s host=%s port=%s username=%s from_address=%s '
            'error_type=%s error_code=%s error_message=%s%s',
            stage,
            self.host,
            self.port,
            self._mask_address(self.username),
            self._mask_address(self.from_email),
            type(exc).__name__,
            getattr(exc, 'smtp_code', None),
            self._safe_error_message(exc),
            f' {detail_string}' if detail_string else '',
        )

    def _log_smtp_success(self, stage: str, **details: str) -> None:
        detail_string = ' '.join(f'{key}={value}' for key, value in details.items())
        logger.info(
            'SMTP diagnostic: stage=%s action=success host=%s port=%s username=%s from_address=%s %s',
            stage,
            self.host,
            self.port,
            self._mask_address(self.username),
            self._mask_address(self.from_email),
            detail_string,
        )

    def _build_message(self, to: str, subject: str, body: str, attachments: list[EmailAttachment] | None = None) -> EmailMessage:
        message = EmailMessage()
        message["To"] = to
        message["Subject"] = subject
        if self.from_name:
            message["From"] = f"{self.from_name} <{self.from_email}>"
        else:
            message["From"] = self.from_email
        message.set_content(body)

        if attachments:
            for filename, content, content_type in attachments:
                maintype, subtype = content_type.split('/', 1) if '/' in content_type else ('application', 'octet-stream')
                message.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

        return message

    def _send_message(self, message: EmailMessage) -> None:
        context = ssl.create_default_context()
        server: smtplib.SMTP | smtplib.SMTP_SSL | None = None
        operation_failed = False
        tls_mode = 'implicit_ssl' if self.port == 465 else ('starttls' if self.use_tls else 'disabled')
        self._log_smtp_start('configuration', tls_mode=tls_mode)
        try:
            self._log_smtp_success('configuration', tls_mode=tls_mode)

            if self.port == 465:
                self._log_smtp_start('connection', tls_mode=tls_mode)
                try:
                    server = smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=20)
                except Exception as exc:
                    self._log_smtp_failure('connection', exc, tls_mode=tls_mode)
                    raise
                self._log_smtp_success('connection', tls_mode=tls_mode)

                self._log_smtp_start('ehlo', tls_mode=tls_mode)
                try:
                    server.ehlo()
                except Exception as exc:
                    self._log_smtp_failure('ehlo', exc, tls_mode=tls_mode)
                    raise
                self._log_smtp_success('ehlo', tls_mode=tls_mode)
            else:
                self._log_smtp_start('connection', tls_mode=tls_mode)
                try:
                    server = smtplib.SMTP(self.host, self.port, timeout=20)
                except Exception as exc:
                    self._log_smtp_failure('connection', exc, tls_mode=tls_mode)
                    raise
                self._log_smtp_success('connection', tls_mode=tls_mode)

                self._log_smtp_start('ehlo', tls_mode=tls_mode)
                try:
                    server.ehlo()
                except Exception as exc:
                    self._log_smtp_failure('ehlo', exc, tls_mode=tls_mode)
                    raise
                self._log_smtp_success('ehlo', tls_mode=tls_mode)

                if self.use_tls:
                    self._log_smtp_start('starttls', tls_mode=tls_mode)
                    try:
                        server.starttls(context=context)
                    except Exception as exc:
                        self._log_smtp_failure('starttls', exc, tls_mode=tls_mode)
                        raise
                    self._log_smtp_success('starttls', tls_mode=tls_mode)

                    self._log_smtp_start('ehlo_post_starttls', tls_mode=tls_mode)
                    try:
                        server.ehlo()
                    except Exception as exc:
                        self._log_smtp_failure('ehlo_post_starttls', exc, tls_mode=tls_mode)
                        raise
                    self._log_smtp_success('ehlo_post_starttls', tls_mode=tls_mode)

            if self.username and self.password:
                self._log_smtp_start('authentication')
                try:
                    server.login(self.username, self.password)
                except Exception as exc:
                    self._log_smtp_failure('authentication', exc)
                    raise
                self._log_smtp_success('authentication')
            else:
                logger.info(
                    'SMTP diagnostic: stage=authentication action=skipped host=%s port=%s username=%s from_address=%s',
                    self.host,
                    self.port,
                    self._mask_address(self.username),
                    self._mask_address(self.from_email),
                )

            self._log_smtp_start('sendmail')
            try:
                server.send_message(message)
            except Exception as exc:
                self._log_smtp_failure('sendmail', exc)
                raise
            self._log_smtp_success('sendmail')
        except Exception:
            operation_failed = True
            raise
        finally:
            if server is not None:
                self._log_smtp_start('quit')
                try:
                    server.quit()
                except Exception as exc:
                    self._log_smtp_failure('quit', exc)
                else:
                    self._log_smtp_success('quit')

    async def send_email(self, to: str, subject: str, body: str, attachments: list[EmailAttachment] | None = None) -> None:
        message = self._build_message(to, subject, body, attachments=attachments)
        try:
            await asyncio.to_thread(self._send_message, message)
        except Exception as exc:
            self._log_smtp_failure('delivery', exc)
            raise
        self._log_smtp_success('delivery')


def get_email_service() -> EmailService:
    if settings.MAIL_HOST and settings.MAIL_FROM:
        return SMTPEmailService(
            host=settings.MAIL_HOST,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            from_email=settings.MAIL_FROM,
            from_name=settings.MAIL_FROM_NAME,
            use_tls=settings.MAIL_USE_TLS,
        )
    return ConsoleEmailService()


def build_registration_confirmation_email(registration_number: str) -> tuple[str, str]:
    subject = "Pragyarambh 2026 - Registration Submitted Successfully"
    body = (
        "Pragyarambh 2026\n\n"
        "Registration Submitted Successfully\n\n"
        f"Registration Number: {registration_number}\n\n"
        "Status: Pending Approval\n\n"
        "Your registration has been successfully received.\n\n"
        "Your details are currently being reviewed by the administration. Once your registration is approved, your official Pragyarambh 2026 entry pass will automatically be sent to this email address.\n\n"
        "Please keep this email for your records."
    )
    return subject, body


def build_registration_approval_email(registration_number: str, pass_number: str) -> tuple[str, str]:
    subject = "Pragyarambh 2026 - Registration Approved"
    body = (
        "Pragyarambh 2026\n\n"
        "Registration Approved\n\n"
        f"Registration Number: {registration_number}\n"
        f"Pass Number: {pass_number}\n\n"
        "Congratulations! Your registration has been approved.\n\n"
        "Your entry pass has been issued and is attached to this email as an image (PNG).\n\n"
        "Status: APPROVED\n\n"
        "Please keep this email for your records."
    )
    return subject, body


def build_registration_rejection_email(registration_number: str, reason: str) -> tuple[str, str]:
    subject = "Pragyarambh 2026 - Registration Review Result"
    body = (
        "Pragyarambh 2026\n\n"
        "Registration Rejected\n\n"
        f"Registration Number: {registration_number}\n\n"
        "We regret to inform you that your registration was not approved.\n\n"
        f"Reason: {reason}\n\n"
        "If you believe this was an error, please contact the event administration team for assistance.\n\n"
        "Thank you for your interest in Pragyarambh 2026."
    )
    return subject, body
