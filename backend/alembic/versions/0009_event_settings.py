"""add event_settings table

Revision ID: 0009_event_settings
Revises: 0008_entry_core
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0009_event_settings'
down_revision = '0008_entry_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_settings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('allow_check_in', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('allow_reentry', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.Column('allow_duplicate_scan', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.Column('require_active_qr', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('require_active_pass', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('require_approved_registration', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('checkin_start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('checkin_end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_entries_per_person', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_event_settings_event_id', 'event_settings', ['event_id'])


def downgrade():
    op.drop_index('ix_event_settings_event_id', table_name='event_settings')
    op.drop_table('event_settings')
