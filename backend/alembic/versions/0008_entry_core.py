"""add gates and entry_logs tables

Revision ID: 0008_entry_core
Revises: 0007_qr_core
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0008_entry_core'
down_revision = '0007_qr_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'gates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1024), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_gates_event_id', 'gates', ['event_id'])

    op.create_table(
        'entry_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pass_id', sa.String(36), sa.ForeignKey('passes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('qr_code_id', sa.String(36), sa.ForeignKey('qrcodes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('gate_id', sa.String(36), sa.ForeignKey('gates.id', ondelete='SET NULL'), nullable=True),
        sa.Column('scanned_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('entry_status', sa.String(50), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('device_identifier', sa.String(255), nullable=True),
        sa.Column('scan_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("entry_status IN ('success','duplicate','revoked','expired','invalid','rejected')", name='ck_entry_logs_status'),
    )


def downgrade():
    op.drop_table('entry_logs')
    op.drop_index('ix_gates_event_id', table_name='gates')
    op.drop_table('gates')
