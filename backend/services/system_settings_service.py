from sqlalchemy.ext.asyncio import AsyncSession

from models.system_settings import SystemSettings
from repos.system_settings_repo import SystemSettingsRepository


class SystemSettingsService:
    def __init__(self, session: AsyncSession):
        self.repo = SystemSettingsRepository(session)
        self.session = session

    async def get_settings(self) -> SystemSettings:
        settings = await self.repo.ensure_settings()
        await self.session.commit()
        return settings

    async def ensure_settings(self) -> SystemSettings:
        settings = await self.repo.ensure_settings()
        await self.session.commit()
        return settings

    async def update_settings(self, changes: dict[str, bool]) -> SystemSettings:
        settings = await self.repo.ensure_settings()
        for field, value in changes.items():
            setattr(settings, field, value)
        await self.repo.update_settings(settings)
        await self.session.commit()
        return settings
