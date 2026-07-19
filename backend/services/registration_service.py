from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.registration import Registration
from repos.registration_repo import RegistrationRepository
from services.registration_number import RegistrationNumberGenerator
from models.registration import RegistrationStatus
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone


class RegistrationService:
    def __init__(self, session: AsyncSession):
        self.repo = RegistrationRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[Registration]:
        return await self.repo.get_by_id(id)

    async def get_by_registration_number(self, registration_number: str) -> Optional[Registration]:
        return await self.repo.get_by_registration_number(registration_number)

    async def get_by_user_and_event(self, user_id: int, event_id: str) -> Optional[Registration]:
        return await self.repo.get_by_user_and_event(user_id, event_id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, reg: Registration) -> Registration:
        r = await self.repo.create(reg)
        await self.session.commit()
        return r

    async def update(self, reg: Registration) -> Registration:
        r = await self.repo.update(reg)
        await self.session.commit()
        return r

    async def delete(self, reg: Registration) -> None:
        await self.repo.delete(reg)
        await self.session.commit()

    async def generate_registration_number(self) -> str:
        # Generate a candidate; caller should assign and commit. This helper returns a candidate string.
        return await RegistrationNumberGenerator.generate_candidate(self.session)

    async def approve_registration(self, registration_id: str, approver_user_id: int) -> Registration:
        reg = await self.repo.get_by_id(registration_id)
        if not reg:
            raise ValueError('Registration not found')
        if reg.status == RegistrationStatus.Approved:
            raise ValueError('Registration already approved')
        if reg.status == 'cancelled':
            raise ValueError('Cannot approve a cancelled registration')

        reg.status = RegistrationStatus.Approved
        reg.approved_by = approver_user_id
        reg.approved_at = datetime.now(timezone.utc)

        # Generate registration_number if missing; ensure uniqueness by retrying on IntegrityError
        if not reg.registration_number:
            max_retries = 5
            for attempt in range(max_retries):
                candidate = await RegistrationNumberGenerator.generate_candidate(self.session)
                reg.registration_number = candidate
                self.session.add(reg)
                try:
                    await self.session.flush()
                    break
                except IntegrityError:
                    await self.session.rollback()
                    # try again
                    if attempt == max_retries - 1:
                        raise

        self.session.add(reg)
        await self.session.commit()
        return reg

    async def reject_registration(self, registration_id: str, approver_user_id: int, reason: str) -> Registration:
        if not reason:
            raise ValueError('Rejected reason is required')
        reg = await self.repo.get_by_id(registration_id)
        if not reg:
            raise ValueError('Registration not found')
        if reg.status == RegistrationStatus.Approved:
            raise ValueError('Cannot reject an approved registration')

        reg.status = RegistrationStatus.Rejected
        reg.rejected_reason = reason
        reg.approved_by = approver_user_id
        reg.approved_at = datetime.now(timezone.utc)

        self.session.add(reg)
        await self.session.commit()
        return reg
