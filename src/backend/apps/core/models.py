from typing import Optional, Union

import orm
from deps import db, models
from ext.orm.fields import ForeignKey

from .constants import BACK_RELATIONS, Gender, RelationType


class Relation(orm.Model):
    tablename = 'relations'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'person_from': ForeignKey(to='Person', on_delete=orm.CASCADE),
        'person_to': ForeignKey(to='Person', on_delete=orm.CASCADE),
        'type': orm.Enum(RelationType),
    }

    def __hash__(self):
        if self.person_from.id > self.person_to.id:
            return hash((self.person_to.id, self.person_from.id))
        return hash((self.person_from.id, self.person_to.id))


def ensure_rel_type(rel_type: Optional[Union[RelationType, str]]) -> RelationType:
    if isinstance(rel_type, RelationType):
        return rel_type
    if not isinstance(rel_type, str):
        raise ValueError(f'Bad relation type: {rel_type}')
    return RelationType(rel_type)


class Person(orm.Model):
    tablename = 'persons'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'name': orm.String(max_length=100),
        'surname': orm.String(max_length=100),
        'patronymic': orm.String(max_length=100, allow_null=True),
        'gender': orm.Enum(Gender),
        'birthname': orm.String(max_length=200, allow_null=True),
        'birthdate': orm.Date(allow_null=True),
        'birthplace': orm.String(max_length=100, allow_null=True),
        'info': orm.Text(allow_null=True),
        'photo': orm.URL(max_length=200,  allow_null=True),
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
        # TODO: check relative is not the same person
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


class Tree(orm.Model):
    tablename = 'trees'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'name': orm.String(max_length=100, default='My tree'),
    }


class UserTree(orm.Model):
    tablename = 'user_tree'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'user': orm.ForeignKey('User', on_delete=orm.CASCADE),
        'tree': orm.ForeignKey(Tree, on_delete=orm.CASCADE),
    }


class PersonTree(orm.Model):
    tablename = 'person_tree'
    registry = models
    fields = {
        'id': orm.Integer(primary_key=True),
        'tree': ForeignKey(to='Tree', on_delete=orm.CASCADE),
        'person': ForeignKey(to='Person', on_delete=orm.CASCADE),
    }
