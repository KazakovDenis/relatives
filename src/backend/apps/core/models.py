from datetime import date
from typing import Optional, Tuple, Union

import ormar
from deps import db, metadata
from ormar import ReferentialAction
from pydantic import HttpUrl

from ..auth.models import User
from .constants import BACK_RELATIONS, Gender, RelationType


def ensure_rel_type(rel_type: Optional[Union[RelationType, str]]) -> RelationType:
    if isinstance(rel_type, RelationType):
        return rel_type
    if not isinstance(rel_type, str):
        raise ValueError(f'Bad relation type: {rel_type}')
    return RelationType(rel_type)


class Person(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'persons'

    id: int = ormar.Integer(primary_key=True)
    # TODO: migrate from name/surname/patronymic to fullname
    name: str = ormar.String(max_length=100)
    surname: str = ormar.String(max_length=100)
    patronymic: Optional[str] = ormar.String(max_length=100, nullable=True)
    gender: Gender = ormar.Enum(enum_class=Gender)
    birthname: Optional[str] = ormar.String(max_length=200, nullable=True)
    birthdate: Optional[date] = ormar.Date(nullable=True)
    birthplace: Optional[str] = ormar.String(max_length=100, nullable=True)
    info: Optional[str] = ormar.Text(nullable=True)
    photo: Optional[HttpUrl] = ormar.String(max_length=200, nullable=True)

    @property
    def fio(self):
        return '%s %s %s' % (self.surname, self.name, self.patronymic or '')

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
        if self.id == person.id:
            return
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
        # todo: This backend does not support multiple-table criteria within DELETE
        await Relation.objects.filter(person_from=self, person_to=person).delete()
        await Relation.objects.filter(person_from=person, person_to=self).delete()


class Tree(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'trees'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100, default='My tree')


# TODO: (user, tree) unique constraint
class UserTree(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'user_tree'

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    tree: Tree = ormar.ForeignKey(Tree, ondelete=ReferentialAction.CASCADE)


class PersonTree(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'person_tree'

    id: int = ormar.Integer(primary_key=True)
    tree: Tree = ormar.ForeignKey(Tree, ondelete=ReferentialAction.CASCADE)
    person: Person = ormar.ForeignKey(Person, ondelete=ReferentialAction.CASCADE)


class Relation(ormar.Model):
    class Meta:
        database = db
        metadata = metadata
        tablename = 'relations'

    id: int = ormar.Integer(primary_key=True)
    person_from: Person = ormar.ForeignKey(Person, ondelete=ReferentialAction.CASCADE, related_name='relations_to')
    person_to: Person = ormar.ForeignKey(Person, ondelete=ReferentialAction.CASCADE, related_name='relations_from')
    type: str = ormar.Enum(enum_class=RelationType)

    def as_tuple(self) -> Tuple[int, int]:
        person_from = getattr(self.person_from, 'id', None)
        person_to = getattr(self.person_to, 'id', None)
        if not person_from or not person_to:
            return person_from, person_to
        if person_from > person_to:
            return person_to, person_from
        return person_from, person_to

    def __hash__(self):
        return hash(self.as_tuple())

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.as_tuple() == other.as_tuple()
