"""Extend Token model.

Revision ID: 78460b24553b
Revises: 77af9d88be6f
Create Date: 2023-01-05 23:15:27.969359

"""
from alembic import op
import sqlalchemy as sa


revision = '78460b24553b'
down_revision = '77af9d88be6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tokens', sa.Column('action', sa.String(length=100), nullable=True))
    op.add_column('tokens', sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('tokens', 'valid_until')
    op.drop_column('tokens', 'action')
