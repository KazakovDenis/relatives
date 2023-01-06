from uuid import UUID

from ..auth.models import User
from .file import copy_person_photo
from .models import Person, PersonTree, Photo, Relation, Tree, UserTree


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
