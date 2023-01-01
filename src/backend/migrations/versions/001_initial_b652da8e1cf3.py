"""Initial.

Revision ID: b652da8e1cf3
Revises:
Create Date: 2022-09-17 23:19:43.982169

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b652da8e1cf3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'trees',
        sa.Column('id', sa.INTEGER(), nullable=True),
        sa.Column('name', sa.VARCHAR(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'persons',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('surname', sa.VARCHAR(length=100), nullable=False),
        sa.Column('patronymic', sa.VARCHAR(length=100), nullable=True),
        sa.Column('gender', sa.VARCHAR(length=6), nullable=False),
        sa.Column('birthname', sa.VARCHAR(length=200), nullable=True),
        sa.Column('birthdate', sa.DATE(), nullable=True),
        sa.Column('birthplace', sa.VARCHAR(length=100), nullable=True),
        sa.Column('info', sa.TEXT(), nullable=True),
        sa.Column('photo', sa.VARCHAR(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'person_tree',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('tree', sa.INTEGER(), nullable=False),
        sa.Column('person', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['person'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tree'], ['trees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'relations',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('person_from', sa.INTEGER(), nullable=False),
        sa.Column('person_to', sa.INTEGER(), nullable=False),
        sa.Column('type', sa.VARCHAR(length=9), nullable=False),
        sa.ForeignKeyConstraint(['person_from'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['person_to'], ['persons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'users',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('email', sa.VARCHAR(length=100), nullable=False),
        sa.Column('password', sa.VARCHAR(length=100), nullable=False),
        sa.Column('is_superuser', sa.BOOLEAN(), nullable=False),
        sa.Column('is_active', sa.BOOLEAN(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table(
        'user_tree',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('user', sa.INTEGER(), nullable=False),
        sa.Column('tree', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['tree'], ['trees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'sessions',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('user', sa.INTEGER(), nullable=False),
        sa.Column('token', sa.CHAR(length=32), nullable=False),
        sa.Column('issued_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sessions_token', 'sessions', ['token'], unique=False)


def downgrade() -> None:
    op.drop_table('sessions')
    op.drop_table('user_tree')
    op.drop_table('users')
    op.drop_table('relations')
    op.drop_table('person_tree')
    op.drop_table('persons')
    op.drop_table('trees')
