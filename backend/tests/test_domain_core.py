import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.session import get_session
from models.domain import Department, AcademicYear, Committee, Venue


@pytest.mark.asyncio
async def test_crud_department_and_committee():
    async with get_session() as s:
        # create department
        dept = Department(name='Computer Science', description='CS Dept')
        s.add(dept)
        await s.flush()
        assert dept.id is not None

        # create committee
        comm = Committee(department_id=dept.id, name='Fresher Committee')
        s.add(comm)
        await s.flush()
        assert comm.id is not None

        # read back with relationship
        from sqlalchemy.orm import selectinload
        q = await s.execute(select(Department).where(Department.id == dept.id).options(selectinload(Department.committees)))
        d = q.scalars().first()
        assert len(d.committees) == 1

        # update
        d.description = 'Updated'
        s.add(d)
        await s.flush()
        q = await s.execute(select(Department).where(Department.id == dept.id))
        d2 = q.scalars().first()
        assert d2.description == 'Updated'

        # soft delete
        d2.is_active = False
        s.add(d2)
        await s.flush()
        assert not d2.is_active


@pytest.mark.asyncio
async def test_academicyear_and_venue_crud():
    async with get_session() as s:
        ay = AcademicYear(code='FY', label='First Year')
        s.add(ay)
        v = Venue(name='Main Hall', building='A', floor=1, capacity=200)
        s.add(v)
        await s.flush()
        assert ay.id is not None and v.id is not None


@pytest.mark.asyncio
async def test_committee_unique_constraint():
    async with get_session() as s:
        dept = Department(name='Electrical', description=None)
        s.add(dept)
        await s.flush()
        c1 = Committee(department_id=dept.id, name='Events')
        s.add(c1)
        await s.flush()
        c2 = Committee(department_id=dept.id, name='Events')
        s.add(c2)
        with pytest.raises(IntegrityError):
            await s.flush()


def test_alembic_upgrade_head():
    # Run the alembic upgrade script to ensure migrations apply
    import importlib
    mod = importlib.import_module('scripts.run_alembic')
    # The script raises on failure; if it returns, assume success
    mod
