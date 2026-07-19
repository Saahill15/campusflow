"""add domain core tables

Revision ID: 0003_domain_core
Revises: 0002_add_tokens
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_domain_core'
down_revision = '0002_add_tokens'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'departments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_departments_name', 'departments', ['name'])

    op.create_table(
        'academic_years',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('label', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_academic_years_code', 'academic_years', ['code'])

    op.create_table(
        'committees',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('committee_head_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('department_id', 'name', name='uq_committee_department_name'),
    )
    op.create_index('ix_committees_department_id', 'committees', ['department_id'])

    op.create_table(
        'venues',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('building', sa.String(200), nullable=True),
        sa.Column('floor', sa.Integer(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_venues_name', 'venues', ['name'])


def downgrade():
    op.drop_index('ix_venues_name', table_name='venues')
    op.drop_table('venues')
    op.drop_index('ix_committees_department_id', table_name='committees')
    # unique constraint was created inline with the table on SQLite, dropping the table will remove it
    op.drop_table('committees')
    op.drop_index('ix_academic_years_code', table_name='academic_years')
    op.drop_table('academic_years')
    op.drop_index('ix_departments_name', table_name='departments')
    op.drop_table('departments')
