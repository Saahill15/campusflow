"""Use TEXT for registration payment proof

Revision ID: 0012_payment_proof_text
Revises: 0011_add_fk_indexes
Create Date: 2026-08-18
"""

from alembic import op
import sqlalchemy as sa

revision = '0012_payment_proof_text'
down_revision = '0011_add_fk_indexes'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE registrations ALTER COLUMN payment_proof TYPE TEXT')
    else:
        op.alter_column('registrations', 'payment_proof', existing_type=sa.String(1024), type_=sa.Text())


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE registrations ALTER COLUMN payment_proof TYPE VARCHAR(1024)')
    else:
        op.alter_column('registrations', 'payment_proof', existing_type=sa.Text(), type_=sa.String(1024))
