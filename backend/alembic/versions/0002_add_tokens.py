"""add verification and password reset tokens

Revision ID: 0002_add_tokens
Revises: 0001_init_auth
Create Date: 2026-07-18
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_add_tokens'
down_revision = '0001_init_auth'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'verification_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('token', sa.String(256), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('used', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('token', sa.String(256), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('used', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
    )


def downgrade():
    op.drop_table('password_reset_tokens')
    op.drop_table('verification_tokens')
