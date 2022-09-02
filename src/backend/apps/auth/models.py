import orm
from deps import models


class User(orm.Model):
    tablename = 'users'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'email': orm.Email(max_length=100, unique=True),
        'password': orm.String(max_length=100),
        'is_superuser': orm.Boolean(default=False),
        'is_active': orm.Boolean(default=True),
    }


class Session(orm.Model):
    tablename = 'sessions'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'user': orm.ForeignKey(User, on_delete=orm.CASCADE),
        'token': orm.UUID(index=True),
        'issued_at': orm.DateTime(),
    }
