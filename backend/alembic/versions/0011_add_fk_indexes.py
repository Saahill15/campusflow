"""Add indexes for commonly queried foreign keys

Revision ID: 0011_add_fk_indexes
Revises: 0010_registration_student_fields
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa

revision = '0011_add_fk_indexes'
down_revision = '0010_registration_student_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_registrations_event_id', 'registrations', ['event_id'])
    op.create_index('ix_passes_event_id', 'passes', ['event_id'])
    op.create_index('ix_qrcodes_pass_id', 'qrcodes', ['pass_id'])
    op.create_index('ix_entry_logs_pass_id', 'entry_logs', ['pass_id'])
    op.create_index('ix_entry_logs_qr_code_id', 'entry_logs', ['qr_code_id'])
    op.create_index('ix_entry_logs_gate_id', 'entry_logs', ['gate_id'])


def downgrade():
    op.drop_index('ix_entry_logs_gate_id', table_name='entry_logs')
    op.drop_index('ix_entry_logs_qr_code_id', table_name='entry_logs')
    op.drop_index('ix_entry_logs_pass_id', table_name='entry_logs')
    op.drop_index('ix_qrcodes_pass_id', table_name='qrcodes')
    op.drop_index('ix_passes_event_id', table_name='passes')
    op.drop_index('ix_registrations_event_id', table_name='registrations')
