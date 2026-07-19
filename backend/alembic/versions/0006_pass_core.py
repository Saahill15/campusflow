"""add passes table

Revision ID: 0006_pass_core
Revises: 0005_registration_core
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0006_pass_core'
down_revision = '0005_registration_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'passes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('registration_id', sa.String(36), sa.ForeignKey('registrations.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('pass_number', sa.String(100), nullable=True, unique=True),
        sa.Column('pass_type', sa.String(50), nullable=False, server_default='general'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending','issued','revoked','used','expired')", name='ck_passes_status'),
        sa.CheckConstraint("pass_type IN ('general','vip','committee','organizer','guest')", name='ck_passes_type'),
    )
    op.create_index('ix_passes_pass_number', 'passes', ['pass_number'])


def downgrade():
    op.drop_index('ix_passes_pass_number', table_name='passes')
    op.drop_table('passes')
