"""Initial

Revision ID: 47f5291659f2
Revises:
Create Date: 2022-08-21 23:13:11.066119

"""
import asyncio

from deps import models


# revision identifiers, used by Alembic.
revision = '47f5291659f2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    asyncio.run(models.create_all())


def downgrade() -> None:
    asyncio.run(models.drop_all())
