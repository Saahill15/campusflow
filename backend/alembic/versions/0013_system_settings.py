"""Create singleton global system settings

Revision ID: 0013_system_settings
Revises: 0012_payment_proof_text
Create Date: 2026-08-19
"""

from alembic import op
import sqlalchemy as sa

revision = '0013_system_settings'
down_revision = '0012_payment_proof_text'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('registration_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('checkin_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('maintenance_mode', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('id = 1', name='ck_system_settings_singleton_id'),
    )
    op.execute(
        sa.text(
            'INSERT INTO system_settings '
            '(id, registration_enabled, checkin_enabled, email_enabled, maintenance_mode) '
            'VALUES (1, TRUE, TRUE, TRUE, FALSE)'
        )
    )


def downgrade():
    op.drop_table('system_settings')
