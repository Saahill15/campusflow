"""Add student detail columns to registrations

Revision ID: 0010_registration_student_fields
Revises: 0009_event_settings
Create Date: 2026-08-10
"""

from alembic import op
import sqlalchemy as sa

revision = '0010_registration_student_fields'
down_revision = '0009_event_settings'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # For non-SQLite DBs, simply alter nullability and add the new columns.
    if bind.dialect.name != 'sqlite':
        op.alter_column('registrations', 'user_id', existing_type=sa.Integer(), nullable=True)
        op.add_column('registrations', sa.Column('first_name', sa.String(150), nullable=True))
        op.add_column('registrations', sa.Column('last_name', sa.String(150), nullable=True))
        op.add_column('registrations', sa.Column('department', sa.String(150), nullable=True))
        op.add_column('registrations', sa.Column('academic_year', sa.String(100), nullable=True))
        op.add_column('registrations', sa.Column('roll_number', sa.String(100), nullable=True))
        op.add_column('registrations', sa.Column('phone', sa.String(50), nullable=True))
        op.add_column('registrations', sa.Column('email', sa.String(255), nullable=True))
        op.add_column('registrations', sa.Column('gender', sa.String(50), nullable=True))
    else:
        # SQLite requires table rebuild to change NOT NULL constraints. Create a new table with
        # user_id nullable and the new student columns, copy data, drop old, and rename.
        op.create_table(
            'registrations_new',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
            sa.Column('first_name', sa.String(150), nullable=True),
            sa.Column('last_name', sa.String(150), nullable=True),
            sa.Column('department', sa.String(150), nullable=True),
            sa.Column('academic_year', sa.String(100), nullable=True),
            sa.Column('roll_number', sa.String(100), nullable=True),
            sa.Column('phone', sa.String(50), nullable=True),
            sa.Column('email', sa.String(255), nullable=True),
            sa.Column('gender', sa.String(50), nullable=True),
            sa.Column('registration_number', sa.String(100), nullable=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
            sa.Column('payment_status', sa.String(50), nullable=False, server_default='not_required'),
            sa.Column('payment_mode', sa.String(100), nullable=True),
            sa.Column('payment_amount', sa.Float(), nullable=True),
            sa.Column('payment_reference', sa.String(255), nullable=True),
            sa.Column('payment_proof', sa.String(1024), nullable=True),
            sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('rejected_reason', sa.Text(), nullable=True),
            sa.Column('checked_in', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
            sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.CheckConstraint("status IN ('pending','approved','rejected','cancelled','checked_in')", name='ck_registrations_status'),
            sa.CheckConstraint("payment_status IN ('not_required','pending','verified','rejected')", name='ck_registrations_payment_status'),
            sa.UniqueConstraint('event_id', 'user_id', name='uq_registration_event_user'),
        )
        # copy existing data; new student columns will be NULL for existing rows
        conn = op.get_bind()
        conn.execute(
            sa.text(
                'INSERT INTO registrations_new (id, event_id, user_id, registration_number, status, payment_status, payment_mode, payment_amount, payment_reference, payment_proof, approved_by, approved_at, rejected_reason, checked_in, checked_in_at, notes, created_at, updated_at, deleted_at) '
                'SELECT id, event_id, user_id, registration_number, status, payment_status, payment_mode, payment_amount, payment_reference, payment_proof, approved_by, approved_at, rejected_reason, checked_in, checked_in_at, notes, created_at, updated_at, deleted_at FROM registrations'
            )
        )
        op.drop_table('registrations')
        op.rename_table('registrations_new', 'registrations')
        op.create_index('ix_registrations_registration_number', 'registrations', ['registration_number'])
        op.create_index('ix_registrations_status', 'registrations', ['status'])


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != 'sqlite':
        # Drop added columns and restore user_id NOT NULL
        op.drop_column('registrations', 'gender')
        op.drop_column('registrations', 'email')
        op.drop_column('registrations', 'phone')
        op.drop_column('registrations', 'roll_number')
        op.drop_column('registrations', 'academic_year')
        op.drop_column('registrations', 'department')
        op.drop_column('registrations', 'last_name')
        op.drop_column('registrations', 'first_name')
        op.alter_column('registrations', 'user_id', existing_type=sa.Integer(), nullable=False)
    else:
        # For SQLite, rebuild the table back to the original shape (without student columns and user_id NOT NULL)
        op.create_table(
            'registrations_old',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('registration_number', sa.String(100), nullable=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
            sa.Column('payment_status', sa.String(50), nullable=False, server_default='not_required'),
            sa.Column('payment_mode', sa.String(100), nullable=True),
            sa.Column('payment_amount', sa.Float(), nullable=True),
            sa.Column('payment_reference', sa.String(255), nullable=True),
            sa.Column('payment_proof', sa.String(1024), nullable=True),
            sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('rejected_reason', sa.Text(), nullable=True),
            sa.Column('checked_in', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
            sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.CheckConstraint("status IN ('pending','approved','rejected','cancelled','checked_in')", name='ck_registrations_status'),
            sa.CheckConstraint("payment_status IN ('not_required','pending','verified','rejected')", name='ck_registrations_payment_status'),
            sa.UniqueConstraint('event_id', 'user_id', name='uq_registration_event_user'),
        )
        conn = op.get_bind()
        # copy matching columns back (student columns are dropped)
        conn.execute(
            sa.text(
                'INSERT INTO registrations_old (id, event_id, user_id, registration_number, status, payment_status, payment_mode, payment_amount, payment_reference, payment_proof, approved_by, approved_at, rejected_reason, checked_in, checked_in_at, notes, created_at, updated_at, deleted_at) '
                'SELECT id, event_id, user_id, registration_number, status, payment_status, payment_mode, payment_amount, payment_reference, payment_proof, approved_by, approved_at, rejected_reason, checked_in, checked_in_at, notes, created_at, updated_at, deleted_at FROM registrations'
            )
        )
        op.drop_table('registrations')
        op.rename_table('registrations_old', 'registrations')
        op.create_index('ix_registrations_registration_number', 'registrations', ['registration_number'])
        op.create_index('ix_registrations_status', 'registrations', ['status'])
