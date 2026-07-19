from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class EmailService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None:
        raise NotImplementedError()


class ConsoleEmailService(EmailService):
    async def send_email(self, to: str, subject: str, body: str) -> None:
        # simple console implementation for dev/test
        logger.info("Sending email to %s: %s", to, subject)
        logger.info("Body:\n%s", body)