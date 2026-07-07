
"""replace audit logs with audit trail

Revision ID: 6a8b7c9d0e1f
Revises: 0e83e6c91c1c
Create Date: 2026-07-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a8b7c9d0e1f'
down_revision = '0e83e6c91c1c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop old table
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    # Create new table
    op.create_table('audit_trails',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=False),
    sa.Column('resource', sa.String(length=100), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('prev_values', sa.JSON(), nullable=True),
    sa.Column('new_values', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_trails_action'), 'audit_trails', ['action'], unique=False)
    op.create_index(op.f('ix_audit_trails_resource'), 'audit_trails', ['resource'], unique=False)
    op.create_index(op.f('ix_audit_trails_timestamp'), 'audit_trails', ['timestamp'], unique=False)

def downgrade() -> None:
    # Drop new table
    op.drop_index(op.f('ix_audit_trails_timestamp'), table_name='audit_trails')
    op.drop_index(op.f('ix_audit_trails_resource'), table_name='audit_trails')
    op.drop_index(op.f('ix_audit_trails_action'), table_name='audit_trails')
    op.drop_table('audit_trails')
    
    # Recreate old table
    op.create_table('audit_logs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
