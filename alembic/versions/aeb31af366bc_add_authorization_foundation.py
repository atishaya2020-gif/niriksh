"""add_authorization_foundation

Revision ID: aeb31af366bc
Revises:
Create Date: 2026-10-03 14:59:14.599467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'aeb31af366bc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'jurisdictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jurisdictions_name'), 'jurisdictions', ['name'], unique=True)
    op.create_index(op.f('ix_jurisdictions_code'), 'jurisdictions', ['code'], unique=True)

    op.create_table(
        'user_jurisdictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('jurisdiction_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'jurisdiction_id', name='uq_user_jurisdictions_user_jurisdiction')
    )
    op.create_index(op.f('ix_user_jurisdictions_jurisdiction_id'), 'user_jurisdictions', ['jurisdiction_id'], unique=False)
    op.create_index(op.f('ix_user_jurisdictions_user_id'), 'user_jurisdictions', ['user_id'], unique=False)

    op.create_table(
        'case_jurisdictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('jurisdiction_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id', 'jurisdiction_id', name='uq_case_jurisdictions_case_jurisdiction')
    )
    op.create_index(op.f('ix_case_jurisdictions_case_id'), 'case_jurisdictions', ['case_id'], unique=False)
    op.create_index(op.f('ix_case_jurisdictions_jurisdiction_id'), 'case_jurisdictions', ['jurisdiction_id'], unique=False)

    op.create_table(
        'case_grants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('capability', sa.String(length=100), nullable=False),
        sa.Column('granted_by', sa.Integer(), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_grants_case_id'), 'case_grants', ['case_id'], unique=False)
    op.create_index(op.f('ix_case_grants_granted_by'), 'case_grants', ['granted_by'], unique=False)
    op.create_index(op.f('ix_case_grants_user_id'), 'case_grants', ['user_id'], unique=False)
    op.create_index(op.f('ix_case_grants_capability'), 'case_grants', ['capability'], unique=False)
    op.create_index(
        'uq_active_user_case_capability',
        'case_grants',
        ['user_id', 'case_id', 'capability'],
        unique=True,
        postgresql_where=sa.text('revoked_at IS NULL')
    )

    op.create_table(
        'cross_state_grants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requesting_user_id', sa.Integer(), nullable=False),
        sa.Column('target_jurisdiction_id', sa.Integer(), nullable=False),
        sa.Column('capability', sa.String(length=100), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['requesting_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_jurisdiction_id'], ['jurisdictions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cross_state_grants_approved_by_id'), 'cross_state_grants', ['approved_by_id'], unique=False)
    op.create_index(op.f('ix_cross_state_grants_capability'), 'cross_state_grants', ['capability'], unique=False)
    op.create_index(op.f('ix_cross_state_grants_requesting_user_id'), 'cross_state_grants', ['requesting_user_id'], unique=False)
    op.create_index(op.f('ix_cross_state_grants_status'), 'cross_state_grants', ['status'], unique=False)
    op.create_index(op.f('ix_cross_state_grants_target_jurisdiction_id'), 'cross_state_grants', ['target_jurisdiction_id'], unique=False)

    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=100), nullable=True),
        sa.Column('target_id', sa.String(length=255), nullable=True),
        sa.Column('case_id', sa.Integer(), nullable=True),
        sa.Column('outcome', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_actor_id'), 'audit_events', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_events_case_id'), 'audit_events', ['case_id'], unique=False)
    op.create_index(op.f('ix_audit_events_event_type'), 'audit_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_events_outcome'), 'audit_events', ['outcome'], unique=False)
    op.create_index(op.f('ix_audit_events_target_id'), 'audit_events', ['target_id'], unique=False)
    op.create_index(op.f('ix_audit_events_target_type'), 'audit_events', ['target_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_events_target_type'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_target_id'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_outcome'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_event_type'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_case_id'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_actor_id'), table_name='audit_events')
    op.drop_table('audit_events')

    op.drop_index(op.f('ix_cross_state_grants_target_jurisdiction_id'), table_name='cross_state_grants')
    op.drop_index(op.f('ix_cross_state_grants_status'), table_name='cross_state_grants')
    op.drop_index(op.f('ix_cross_state_grants_requesting_user_id'), table_name='cross_state_grants')
    op.drop_index(op.f('ix_cross_state_grants_capability'), table_name='cross_state_grants')
    op.drop_index(op.f('ix_cross_state_grants_approved_by_id'), table_name='cross_state_grants')
    op.drop_table('cross_state_grants')

    op.drop_index('uq_active_user_case_capability', table_name='case_grants')
    op.drop_index(op.f('ix_case_grants_capability'), table_name='case_grants')
    op.drop_index(op.f('ix_case_grants_user_id'), table_name='case_grants')
    op.drop_index(op.f('ix_case_grants_granted_by'), table_name='case_grants')
    op.drop_index(op.f('ix_case_grants_case_id'), table_name='case_grants')
    op.drop_table('case_grants')

    op.drop_index(op.f('ix_case_jurisdictions_jurisdiction_id'), table_name='case_jurisdictions')
    op.drop_index(op.f('ix_case_jurisdictions_case_id'), table_name='case_jurisdictions')
    op.drop_table('case_jurisdictions')

    op.drop_index(op.f('ix_user_jurisdictions_user_id'), table_name='user_jurisdictions')
    op.drop_index(op.f('ix_user_jurisdictions_jurisdiction_id'), table_name='user_jurisdictions')
    op.drop_table('user_jurisdictions')

    op.drop_index(op.f('ix_jurisdictions_code'), table_name='jurisdictions')
    op.drop_index(op.f('ix_jurisdictions_name'), table_name='jurisdictions')
    op.drop_table('jurisdictions')
