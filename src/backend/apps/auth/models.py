import orm
from deps import models


class User(orm.Model):
    tablename = 'users'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'email': orm.Email(max_length=100, unique=True),
        'password': orm.String(max_length=100),
    }
