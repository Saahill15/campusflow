"""add events table

Revision ID: 0004_event_core
Revises: 0003_domain_core
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_event_core'
down_revision = '0003_domain_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('slug', sa.String(300), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('banner_image', sa.String(1024), nullable=True),
        sa.Column('start_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('registration_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('registration_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('venue_id', sa.String(36), sa.ForeignKey('venues.id', ondelete='SET NULL'), nullable=True),
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('academic_year_id', sa.String(36), sa.ForeignKey('academic_years.id', ondelete='SET NULL'), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('registered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('visibility', sa.String(50), nullable=False, server_default='public'),
        sa.Column('allow_waitlist', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('requires_payment', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.CheckConstraint("status IN ('draft','published','registration_open','registration_closed','ongoing','completed','cancelled')", name='ck_events_status'),
        sa.CheckConstraint("visibility IN ('public','private','department_only')", name='ck_events_visibility'),
    )
    op.create_index('ix_events_slug', 'events', ['slug'])
    op.create_index('ix_events_start', 'events', ['start_datetime'])
    op.create_index('ix_events_status', 'events', ['status'])


def downgrade():
    op.drop_index('ix_events_status', table_name='events')
    op.drop_index('ix_events_start', table_name='events')
    op.drop_index('ix_events_slug', table_name='events')
    op.drop_table('events')
