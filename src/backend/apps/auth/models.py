from datetime import datetime

import ormar
from deps import db, metadata
from ormar import ReferentialAction


class User(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'users'

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=100, unique=True)
    password: str = ormar.String(max_length=100)
    is_superuser: str = ormar.Boolean(default=False, nullable=False)
    is_active: str = ormar.Boolean(default=False, nullable=False)


class Session(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'sessions'

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE, nullable=False)
    token: str = ormar.UUID(index=True)
    issued_at: datetime = ormar.DateTime()
