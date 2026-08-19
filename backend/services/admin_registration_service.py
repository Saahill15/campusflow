from datetime import date, datetime, time, timedelta, timezone
import re
from typing import Optional, Sequence, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.registration import PaymentStatus, Registration, RegistrationStatus
from models.pass_model import Pass
from schemas.admin import (
    AdminDashboardCount,
    AdminDashboardRecentRegistration,
    AdminDashboardResponse,
    AdminRegistrationFilterOptions,
    AdminRegistrationItem,
)


class AdminRegistrationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(
        self,
        query,
        status: Optional[str],
        search: Optional[str],
        payment_status: Optional[str] = None,
        department: Optional[str] = None,
        academic_year: Optional[str] = None,
        checked_in: Optional[bool] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
        conditions = []
        if status and status != 'all':
            conditions.append(Registration.status == status)
        if payment_status and payment_status != 'all':
            conditions.append(Registration.payment_status == payment_status)
        if department and department != 'all':
            conditions.append(Registration.department == department)
        if academic_year and academic_year != 'all':
            conditions.append(Registration.academic_year == academic_year)
        if checked_in is not None:
            check_in_condition = or_(Registration.checked_in.is_(True), Pass.checked_in_at.is_not(None))
            conditions.append(check_in_condition if checked_in else ~check_in_condition)
        if date_from:
            conditions.append(Registration.created_at >= datetime.combine(date_from, time.min, tzinfo=timezone.utc))
        if date_to:
            conditions.append(Registration.created_at < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc))
        if search:
            term = f'%{search.strip()}%'
            conditions.append(
                or_(
                    Registration.registration_number.ilike(term),
                    Registration.first_name.ilike(term),
                    Registration.last_name.ilike(term),
                    Registration.roll_number.ilike(term),
                    Registration.email.ilike(term),
                    Pass.pass_number.ilike(term),
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
        payment_status: Optional[str] = None,
        department: Optional[str] = None,
        academic_year: Optional[str] = None,
        checked_in: Optional[bool] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> Tuple[Sequence[AdminRegistrationItem], int, AdminRegistrationFilterOptions]:
        base_query = select(Registration, Pass).outerjoin(Pass, Pass.registration_id == Registration.id)
        filtered_query = self._apply_filters(
            base_query,
            status,
            search,
            payment_status,
            department,
            academic_year,
            checked_in,
            date_from,
            date_to,
        )
        count_query = select(func.count()).select_from(filtered_query.subquery())
        total = int((await self.session.execute(count_query)).scalar_one())

        offset = (page - 1) * per_page
        items_query = filtered_query.order_by(Registration.created_at.desc(), Registration.id.desc()).limit(per_page).offset(offset)
        rows = (await self.session.execute(items_query)).all()
        items = [
            AdminRegistrationItem(
                id=registration.id,
                registration_number=registration.registration_number,
                first_name=registration.first_name,
                last_name=registration.last_name,
                department=registration.department,
                academic_year=registration.academic_year,
                roll_number=registration.roll_number,
                phone=registration.phone,
                email=registration.email,
                gender=registration.gender,
                status=registration.status,
                payment_status=registration.payment_status,
                pass_number=pass_obj.pass_number if pass_obj else None,
                pass_status=pass_obj.status if pass_obj else None,
                checked_in=bool(registration.checked_in or (pass_obj and pass_obj.checked_in_at)),
                created_at=registration.created_at,
                approved_by=registration.approved_by,
                approved_at=registration.approved_at,
                rejected_reason=registration.rejected_reason,
            )
            for registration, pass_obj in rows
        ]

        departments = (await self.session.execute(
            select(Registration.department)
            .where(Registration.department.is_not(None))
            .distinct()
            .order_by(Registration.department.asc())
        )).scalars().all()
        academic_years = (await self.session.execute(
            select(Registration.academic_year)
            .where(Registration.academic_year.is_not(None))
            .distinct()
            .order_by(Registration.academic_year.asc())
        )).scalars().all()
        filter_options = AdminRegistrationFilterOptions(
            departments=list(departments),
            academic_years=list(academic_years),
            payment_statuses=[PaymentStatus.NotRequired, PaymentStatus.Pending, PaymentStatus.Verified, PaymentStatus.Rejected],
        )
        return items, total, filter_options

    async def get_registration(self, registration_id: str) -> Optional[Registration]:
        result = await self.session.execute(select(Registration).where(Registration.id == registration_id))
        return result.scalars().first()

    async def update_registration(self, registration_id: str, changes: dict) -> Registration:
        registration = await self.get_registration(registration_id)
        if not registration:
            raise ValueError('Registration not found')

        if 'first_name' in changes:
            value = (changes['first_name'] or '').strip()
            if not value:
                raise ValueError('First name is required')
            registration.first_name = ' '.join(part[:1].upper() + part[1:].lower() for part in value.split())
        if 'last_name' in changes:
            value = (changes['last_name'] or '').strip()
            if not value:
                raise ValueError('Last name is required')
            registration.last_name = ' '.join(part[:1].upper() + part[1:].lower() for part in value.split())
        if 'department' in changes:
            value = (changes['department'] or '').strip()
            if value not in {
                'Cybersecurity and Digital Forensics',
                'Data Science and Data Analysis',
                'Artificial Intelligence and Machine Learning',
            }:
                raise ValueError('Department is invalid')
            registration.department = value
        if 'academic_year' in changes:
            value = (changes['academic_year'] or '').strip()
            if value not in {'First Year', 'Second Year', 'Third Year'}:
                raise ValueError('Academic year is invalid')
            registration.academic_year = value
        if 'roll_number' in changes:
            value = (changes['roll_number'] or '').strip().upper()
            if not value:
                raise ValueError('Roll number is required')
            if await self._find_duplicate(registration, 'roll_number', value):
                raise ValueError('duplicate_roll_number')
            registration.roll_number = value
        if 'phone' in changes:
            value = (changes['phone'] or '').strip()
            cleaned = value.replace(' ', '').replace('-', '')
            if not cleaned.isdigit() or len(cleaned) < 7:
                raise ValueError('Phone number must contain at least 7 digits')
            registration.phone = value
        if 'email' in changes:
            value = (changes['email'] or '').strip().lower()
            if not value or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value):
                raise ValueError('Please enter a valid email address')
            if await self._find_duplicate(registration, 'email', value):
                raise ValueError('duplicate_email')
            registration.email = value
        if 'gender' in changes:
            value = (changes['gender'] or '').strip()
            if value not in {'Male', 'Female', 'Other'}:
                raise ValueError('Gender is invalid')
            registration.gender = value
        if 'notes' in changes:
            registration.notes = changes['notes'].strip() if changes['notes'] else None

        self.session.add(registration)
        await self.session.commit()
        await self.session.refresh(registration)
        return registration

    async def _find_duplicate(self, registration: Registration, field: str, value: str) -> Optional[Registration]:
        query = select(Registration).where(
            Registration.event_id == registration.event_id,
            getattr(Registration, field) == value,
            Registration.id != registration.id,
            Registration.status.in_([
                RegistrationStatus.Pending,
                RegistrationStatus.Approved,
                RegistrationStatus.Cancelled,
                RegistrationStatus.CheckedIn,
            ]),
        )
        return (await self.session.execute(query)).scalars().first()

    async def get_dashboard_summary(self, recent_limit: int = 6) -> AdminDashboardResponse:
        base_filter = Registration.deleted_at.is_(None)

        total = int((await self.session.execute(
            select(func.count()).select_from(Registration).where(base_filter)
        )).scalar_one())

        status_counts = {
            status: int(count)
            for status, count in (await self.session.execute(
                select(Registration.status, func.count())
                .where(base_filter)
                .group_by(Registration.status)
            )).all()
        }

        checked_in = int((await self.session.execute(
            select(func.count()).select_from(Registration).where(base_filter, Registration.checked_in.is_(True))
        )).scalar_one())

        payment_counts = {
            payment_status: int(count)
            for payment_status, count in (await self.session.execute(
                select(Registration.payment_status, func.count())
                .where(base_filter)
                .group_by(Registration.payment_status)
            )).all()
        }

        department_rows = (await self.session.execute(
            select(Registration.department, func.count())
            .where(base_filter)
            .group_by(Registration.department)
            .order_by(func.count().desc(), Registration.department.asc())
        )).all()
        department_counts = {department or 'Unspecified': int(count) for department, count in department_rows}
        required_departments = [
            'Cybersecurity and Digital Forensics',
            'Artificial Intelligence and Machine Learning',
            'Data Science and Data Analysis',
        ]
        department_overview = [
            AdminDashboardCount(label=department, count=department_counts.pop(department, 0))
            for department in required_departments
        ]
        department_overview.extend(
            AdminDashboardCount(label=department, count=count)
            for department, count in sorted(department_counts.items(), key=lambda item: (-item[1], item[0]))
        )

        academic_year_rows = (await self.session.execute(
            select(Registration.academic_year, func.count())
            .where(base_filter)
            .group_by(Registration.academic_year)
            .order_by(func.count().desc(), Registration.academic_year.asc())
        )).all()

        recent_rows = (await self.session.execute(
            select(Registration)
            .where(base_filter)
            .order_by(Registration.created_at.desc(), Registration.id.desc())
            .limit(recent_limit)
        )).scalars().all()

        return AdminDashboardResponse(
            total_registrations=total,
            pending_approval=status_counts.get(RegistrationStatus.Pending, 0),
            approved=status_counts.get(RegistrationStatus.Approved, 0),
            rejected=status_counts.get(RegistrationStatus.Rejected, 0),
            checked_in=checked_in,
            not_checked_in=total - checked_in,
            recent_registrations=[
                AdminDashboardRecentRegistration(
                    registration_number=registration.registration_number,
                    student_name=' '.join(filter(None, [registration.first_name, registration.last_name])) or 'Unnamed student',
                    department=registration.department,
                    status=registration.status,
                    created_at=registration.created_at,
                )
                for registration in recent_rows
            ],
            department_overview=department_overview,
            academic_year_overview=[
                AdminDashboardCount(label=academic_year or 'Unspecified', count=int(count))
                for academic_year, count in academic_year_rows
            ],
            payment_overview=[
                AdminDashboardCount(label='Paid', count=payment_counts.get(PaymentStatus.Verified, 0)),
                AdminDashboardCount(label='Pending', count=payment_counts.get(PaymentStatus.Pending, 0)),
                AdminDashboardCount(label='Not Required', count=payment_counts.get(PaymentStatus.NotRequired, 0)),
            ],
        )
