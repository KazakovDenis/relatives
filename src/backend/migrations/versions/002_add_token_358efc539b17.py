"""Add token.

Revision ID: 358efc539b17
Revises: b652da8e1cf3
Create Date: 2022-11-03 00:11:53.170999

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '358efc539b17'
down_revision = 'b652da8e1cf3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('user_tree') as batch_op:
        batch_op.add_column(sa.Column('is_owner', sa.Boolean, default=False))
    op.create_table(
        'tokens',
        sa.Column('token', UUID(as_uuid=True), autoincrement=False, server_default=func.gen_random_uuid()),
        sa.PrimaryKeyConstraint('token', name='tokens_pkey'),
    )


def downgrade() -> None:
    op.drop_table('tokens')
    with op.batch_alter_table('user_tree') as batch_op:
        batch_op.drop_column('is_owner')
