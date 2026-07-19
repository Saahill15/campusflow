from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.qr_code import QRCode
from repos.qr_repo import QRCodeRepository


class QRCodeService:
    def __init__(self, session: AsyncSession):
        self.repo = QRCodeRepository(session)
        self.session = session

    async def get(self, id: str) -> Optional[QRCode]:
        return await self.repo.get_by_id(id)

    async def get_by_token(self, token: str) -> Optional[QRCode]:
        return await self.repo.get_by_token(token)

    async def get_by_pass(self, pass_id: str) -> Optional[QRCode]:
        return await self.repo.get_by_pass(pass_id)

    async def list(self, limit: int = 100, offset: int = 0):
        return await self.repo.list(limit=limit, offset=offset)

    async def create(self, qrcode: QRCode) -> QRCode:
        qrcode = await self.repo.create(qrcode)
        await self.session.commit()
        return qrcode

    async def update(self, qrcode: QRCode) -> QRCode:
        qrcode = await self.repo.update(qrcode)
        await self.session.commit()
        return qrcode

    async def delete(self, qrcode: QRCode) -> None:
        await self.repo.delete(qrcode)
        await self.session.commit()
