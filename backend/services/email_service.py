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
        if self.port == 465:
            with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=20) as server:
                server.ehlo()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(message)
        else:
            with smtplib.SMTP(self.host, self.port, timeout=20) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls(context=context)
                    server.ehlo()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(message)

    async def send_email(self, to: str, subject: str, body: str, attachments: list[EmailAttachment] | None = None) -> None:
        message = self._build_message(to, subject, body, attachments=attachments)
        await asyncio.to_thread(self._send_message, message)


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