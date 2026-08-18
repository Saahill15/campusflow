from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.system_settings import SystemSettings


class SystemSettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> SystemSettings | None:
        result = await self.session.execute(select(SystemSettings).where(SystemSettings.id == 1))
        return result.scalars().first()

    async def ensure_settings(self) -> SystemSettings:
        settings = await self.get_settings()
        if settings:
            return settings

        settings = SystemSettings(id=1)
        self.session.add(settings)
        await self.session.flush()
        return settings

    async def update_settings(self, settings: SystemSettings) -> SystemSettings:
        self.session.add(settings)
        await self.session.flush()
        return settings
