import orm

from ext.orm.fields import ForeignKey
from .init import models


class Person(orm.Model):
    tablename = 'persons'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'name': orm.String(max_length=100),
        'surname': orm.String(max_length=100),
        'patronymic': orm.String(max_length=100, allow_null=True),
        'birthdate': orm.Date(allow_null=True),
        'birthplace': orm.String(max_length=100, allow_null=True),
        'info': orm.Text(allow_null=True),
        'father': ForeignKey(to='Person', allow_null=True, on_delete=orm.SET_NULL),
        'mother': ForeignKey(to='Person', allow_null=True, on_delete=orm.SET_NULL),
    }
