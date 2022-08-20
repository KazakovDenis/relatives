from typing import Optional, Union

import orm

from deps import models, db
from ext.orm.fields import ForeignKey
from .constants import BACK_RELATIONS, Gender, RelationType
from .utils import ensure_rel_type


class Relation(orm.Model):
    tablename = 'relations'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'person_from': ForeignKey(to='Person', on_delete=orm.CASCADE),
        'person_to': ForeignKey(to='Person', on_delete=orm.CASCADE),
        'type': orm.Enum(RelationType),
    }


class Person(orm.Model):
    tablename = 'persons'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'name': orm.String(max_length=100),
        'surname': orm.String(max_length=100),
        'patronymic': orm.String(max_length=100, allow_null=True),
        'gender': orm.Enum(Gender),
        'birthdate': orm.Date(allow_null=True),
        'birthplace': orm.String(max_length=100, allow_null=True),
        'info': orm.Text(allow_null=True),
    }

    async def get_relatives(self, rel_type: Optional[Union[RelationType, str]] = None) -> list['Person']:
        if rel_type:
            rel_type = ensure_rel_type(rel_type)
            rels = await Relation.objects.all(person_from=self, type=rel_type.value)
        else:
            rels = await Relation.objects.all(person_from=self)
        pids = [rel.person_to.id for rel in rels]
        return await Person.objects.filter(id__in=pids).all()

    @db.transaction()
    async def add_relative(self, rel_type: RelationType, person: 'Person'):
        rel_type = ensure_rel_type(rel_type)
        await Relation.objects.get_or_create(
            {},
            person_from=self,
            person_to=person,
            type=rel_type.value,
        )
        await Relation.objects.get_or_create(
            {},
            person_from=person,
            person_to=self,
            type=BACK_RELATIONS[rel_type].value,
        )

    @db.transaction()
    async def remove_relative(self, person: 'Person'):
        await Relation.objects.filter(person_from=self, person_to=person).delete()
        await Relation.objects.filter(person_from=person, person_to=self).delete()
