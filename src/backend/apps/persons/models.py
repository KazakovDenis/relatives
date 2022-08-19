import orm

from ext.orm.fields import ForeignKey
from deps import models
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

    async def get_relatives(self, rel_type: RelationType) -> list['Person']:
        self.ensure_rel_type(rel_type)
        rels = await Relation.objects.all(person_from=self, type=rel_type.value)
        pids = [rel.person_to.id for rel in rels]
        return await Person.objects.filter(id__in=pids).all()

    async def add_relative(self, rel_type: RelationType, person: 'Person'):
        self.ensure_rel_type(rel_type)
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

    async def remove_relative(self, person: 'Person'):
        await Relation.objects.filter(person_from=self, person_to=person).delete()
        await Relation.objects.filter(person_from=person, person_to=self).delete()

    @staticmethod
    def ensure_rel_type(rel_type: RelationType):
        if not isinstance(rel_type, RelationType):
            raise ValueError(f'Bad relation type: {rel_type}')
