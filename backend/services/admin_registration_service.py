from typing import Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.registration import Registration


class AdminRegistrationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(self, query, status: Optional[str], search: Optional[str]):
        conditions = []
        if status and status != 'all':
            conditions.append(Registration.status == status)
        if search:
            term = f'%{search.strip()}%'
            conditions.append(
                or_(
                    Registration.registration_number.ilike(term),
                    Registration.first_name.ilike(term),
                    Registration.last_name.ilike(term),
                    Registration.roll_number.ilike(term),
                    Registration.email.ilike(term),
                )
            )
        if conditions:
            query = query.where(and_(*conditions))
        return query

    async def list_registrations(
        self,
        *,
        page: int,
        per_page: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[Sequence[Registration], int]:
        base_query = select(Registration)
        filtered_query = self._apply_filters(base_query, status, search)

        count_query = select(func.count()).select_from(filtered_query.subquery())
        total = int((await self.session.execute(count_query)).scalar_one())

        offset = (page - 1) * per_page
        items_query = filtered_query.order_by(Registration.created_at.desc(), Registration.id.desc()).limit(per_page).offset(offset)
        items = (await self.session.execute(items_query)).scalars().all()
        return items, total

    async def get_registration(self, registration_id: str) -> Optional[Registration]:
        result = await self.session.execute(select(Registration).where(Registration.id == registration_id))
        return result.scalars().first()
