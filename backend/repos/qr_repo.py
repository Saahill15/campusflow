from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.qr_code import QRCode


class QRCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: str) -> Optional[QRCode]:
        q = await self.session.execute(select(QRCode).where(QRCode.id == id))
        return q.scalars().first()

    async def get_by_token(self, token: str) -> Optional[QRCode]:
        q = await self.session.execute(select(QRCode).where(QRCode.qr_token == token))
        return q.scalars().first()

    async def get_by_pass(self, pass_id: str) -> Optional[QRCode]:
        q = await self.session.execute(select(QRCode).where(QRCode.pass_id == pass_id))
        return q.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[QRCode]:
        q = await self.session.execute(select(QRCode).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, qrcode: QRCode) -> QRCode:
        self.session.add(qrcode)
        await self.session.flush()
        return qrcode

    async def update(self, qrcode: QRCode) -> QRCode:
        self.session.add(qrcode)
        await self.session.flush()
        return qrcode

    async def delete(self, qrcode: QRCode) -> None:
        await self.session.delete(qrcode)
        await self.session.flush()
