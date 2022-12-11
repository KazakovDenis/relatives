"""Correct models to fit Alembic schema.

Revision ID: bafe5b384431
Revises: 5ac70b3bd542
Create Date: 2022-12-11 23:42:24.420838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bafe5b384431'
down_revision = '5ac70b3bd542'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('sessions_user_fkey', 'sessions', type_='foreignkey')
    op.create_foreign_key('fk_sessions_users_id_user', 'sessions', 'users', ['user'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uc_user_tree_user_tree', 'user_tree', ['user', 'tree'])
    op.create_unique_constraint('uc_person_tree_person_tree', 'person_tree', ['person', 'tree'])
    op.create_unique_constraint('uc_relations_person_from_person_to', 'relations', ['person_from', 'person_to'])


def downgrade() -> None:
    op.drop_constraint('uc_person_tree_person_tree', 'person_tree', type_='unique')
    op.drop_constraint('uc_relations_person_from_person_to', 'relations', type_='unique')
    op.drop_constraint('uc_user_tree_user_tree', 'user_tree', type_='unique')
    op.drop_constraint('fk_sessions_users_id_user', 'sessions', type_='foreignkey')
    op.create_foreign_key('sessions_user_fkey', 'sessions', 'users', ['user'], ['id'], ondelete='SET NULL')
