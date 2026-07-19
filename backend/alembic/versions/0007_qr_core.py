"""add qrcodes table

Revision ID: 0007_qr_core
Revises: 0006_pass_core
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0007_qr_core'
down_revision = '0006_pass_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'qrcodes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('pass_id', sa.String(36), sa.ForeignKey('passes.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('qr_token', sa.String(255), nullable=True, unique=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_scanned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scan_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending','active','revoked','expired')", name='ck_qrcodes_status'),
    )
    op.create_index('ix_qrcodes_qr_token', 'qrcodes', ['qr_token'])


def downgrade():
    op.drop_index('ix_qrcodes_qr_token', table_name='qrcodes')
    op.drop_table('qrcodes')
