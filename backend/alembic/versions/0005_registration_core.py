"""add registrations table

Revision ID: 0005_registration_core
Revises: 0004_event_core
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0005_registration_core'
down_revision = '0004_event_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'registrations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('registration_number', sa.String(100), nullable=True, unique=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('payment_status', sa.String(50), nullable=False, server_default='not_required'),
        sa.Column('payment_mode', sa.String(100), nullable=True),
        sa.Column('payment_amount', sa.Float(), nullable=True),
        sa.Column('payment_reference', sa.String(255), nullable=True),
        sa.Column('payment_proof', sa.String(1024), nullable=True),
        sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_reason', sa.Text(), nullable=True),
        sa.Column('checked_in', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending','approved','rejected','cancelled','checked_in')", name='ck_registrations_status'),
        sa.CheckConstraint("payment_status IN ('not_required','pending','verified','rejected')", name='ck_registrations_payment_status'),
        sa.UniqueConstraint('event_id', 'user_id', name='uq_registration_event_user'),
    )
    op.create_index('ix_registrations_registration_number', 'registrations', ['registration_number'])
    op.create_index('ix_registrations_status', 'registrations', ['status'])


def downgrade():
    op.drop_index('ix_registrations_status', table_name='registrations')
    op.drop_index('ix_registrations_registration_number', table_name='registrations')
    op.drop_table('registrations')
