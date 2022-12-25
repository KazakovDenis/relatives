"""Add User & Tree to Token.

Revision ID: 77af9d88be6f
Revises: bafe5b384431
Create Date: 2022-12-26 00:32:48.365249

"""
from alembic import op
import sqlalchemy as sa


revision = '77af9d88be6f'
down_revision = 'bafe5b384431'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tokens', sa.Column('user', sa.Integer(), nullable=True))
    op.add_column('tokens', sa.Column('tree', sa.Integer(), nullable=True))
    op.create_unique_constraint('uc_tokens_user_tree', 'tokens', ['user', 'tree'])
    op.create_foreign_key('fk_tokens_users_id_user', 'tokens', 'users', ['user'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_tokens_trees_id_tree', 'tokens', 'trees', ['tree'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('fk_tokens_trees_id_tree', 'tokens', type_='foreignkey')
    op.drop_constraint('fk_tokens_users_id_user', 'tokens', type_='foreignkey')
    op.drop_constraint('uc_tokens_user_tree', 'tokens', type_='unique')
    op.drop_column('tokens', 'tree')
    op.drop_column('tokens', 'user')
