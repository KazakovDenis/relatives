from typing import Tuple
from uuid import UUID

import aiofiles
import pydantic
from aiocsv import AsyncDictReader
from ormar import NoMatch

from ..auth.models import User
from .constants import RelationType
from .file import copy_person_photo
from .models import Person, PersonTree, Photo, Relation, Tree, UserTree
from .schemas import PersonSchema


async def load_persons_csv(filename: str) -> Tuple[int, int]:
    """Load person data from a CSV-file."""
    loaded = errors = 0

    async with aiofiles.open(filename) as f:
        async for row in AsyncDictReader(f):
            row['birthdate'] = row['birthdate'] or None
            try:
                validated = PersonSchema(**row)
                person = await Person.objects.create(**validated.dict())
                loaded += 1
            except pydantic.ValidationError:
                errors += 1
                continue

            for person_id, relation in [
                (row['mother'], RelationType.PARENT),
                (row['father'], RelationType.PARENT),
                (row['spouse'], RelationType.SPOUSE),
                *[
                    (ex_spouse_id, RelationType.EX_SPOUSE)
                    for ex_spouse_id in row['ex_spouse'].split(',')
                ],
                *[
                   (child_id, RelationType.CHILD)
                    for child_id in row['children'].split(',')
                ],

            ]:
                if not person_id:
                    continue
                try:
                    relative = await Person.objects.get(id=int(person_id))
                    await person.add_relative(relation, relative)
                except (ValueError, NoMatch):
                    pass

    return loaded, errors


def str_to_uuid(token: str) -> UUID | None:
    try:
        return UUID(token)
    except ValueError:
        return None


async def copy_tree(user: User, old: Tree, new_name: str) -> Tree:
    new_tree = await Tree.objects.create(name=new_name)
    await UserTree.objects.create(user=user, tree=new_tree, is_owner=True)

    # Process persons
    persons_map = {}
    pt_batch = []

    for person in await Person.objects.all(persontrees__tree=old):
        exclude = person.extract_related_names() ^ {'id'}
        # we need id, bulk_create does not provide it
        new_person = await Person.objects.create(**person.dict(exclude=exclude))
        persons_map[person.id] = new_person
        pt_batch.append(PersonTree(tree=new_tree, person=new_person))

    await PersonTree.objects.bulk_create(pt_batch)

    # Process relations
    rel_batch = []

    for pid in persons_map:
        for relation in await Relation.objects.all(person_from=pid):
            rel_batch.append(Relation(
                person_from=persons_map[pid],
                person_to=persons_map[relation.person_to.id],
                type=relation.type,
            ))

    await Relation.objects.bulk_create(rel_batch)

    # Process photos
    ph_batch = []

    for pid in persons_map:
        for old_photo in await Photo.objects.all(person__id=pid):
            new_photo = copy_person_photo(old_photo, persons_map[pid])
            ph_batch.append(new_photo)

    await Photo.objects.bulk_create(ph_batch)
    return new_tree
