"""Add photo model.

Revision ID: 5ac70b3bd542
Revises: 358efc539b17
Create Date: 2022-12-05 00:09:08.111914

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '5ac70b3bd542'
down_revision = '358efc539b17'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'photos',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('location', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
        sa.Column('person', sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['person'], ['persons.id'], ondelete='CASCADE'),
    )
    op.drop_column('persons', 'photo')


def downgrade() -> None:
    op.add_column('persons', sa.Column('photo', sa.VARCHAR(length=200), nullable=True))
    op.drop_table('photos')
