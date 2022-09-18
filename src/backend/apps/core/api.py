from fastapi import APIRouter, HTTPException, Query, Security, status
from fastapi.responses import Response
from ormar import MultipleMatches, NoMatch

from ..auth.models import User
from ..auth.utils import get_user
from .constants import BACK_RELATIONS, RelationType
from .models import Person, PersonTree, Relation, Tree, UserTree
from .permissions import has_tree_perm
from .schemas import PersonSchema, RelationSchema, TreeSchema


router = APIRouter()


@router.get('/tree')
async def tree_list(user: User = Security(get_user)):
    uts = await UserTree.objects.select_related('tree').all(user=user)
    return [ut.tree for ut in uts]


@router.post('/tree')
async def tree_create(response: Response, tree: TreeSchema, user: User = Security(get_user)):
    ut = await UserTree.objects.select_related('tree').get_or_none(user=user, tree__name=tree.name)
    if ut:
        tree_obj = ut.tree
        response.status_code = status.HTTP_200_OK
    else:
        tree_obj = await Tree.objects.create(**tree.dict())
        await UserTree.objects.create(user=user, tree=tree_obj)
        response.status_code = status.HTTP_201_CREATED
    return tree_obj


@router.get('/tree/{tid}')
async def tree_detail(tid: int, user: User = Security(get_user)):
    if not (tree := await has_tree_perm(user.id, tid)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not tree:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return tree


@router.get('/tree/{tid}/scheme')
async def tree_scheme(tid: int, user: User = Security(get_user)):
    if not (tree := await has_tree_perm(user.id, tid)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    persons = await Person.objects.all(persontrees__tree=tree)
    rels = (
        await Relation.objects
        .exclude(type=RelationType.CHILD)
        .all(person_from__in=[p.id for p in persons])
    )
    return {
        'nodes': persons,
        'edges': list({rel for rel in rels}),
    }


@router.post('/tree/{tree_id}/persons')
async def person_create(person: PersonSchema, tree_id: int, user: User = Security(get_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not tree:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Tree not found')

    person = await Person.objects.create(**person.dict())
    await PersonTree.objects.create(tree=tree, person=person)
    return person


@router.get('/tree/{tree_id}/persons')
async def person_list(tree_id: int, q: str = Query(''), user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if not q:
        return []

    q = q.split(maxsplit=2)
    if len(q) == 3:
        where = {
            'surname__icontains': q[0],
            'name__icontains': q[1],
            'patronymic__icontains': q[2],
        }
    elif len(q) == 2:
        where = {
            'surname__icontains': q[0],
            'name__icontains': q[1],
        }
    else:
        where = {'surname__icontains': q[0]}

    return await Person.objects.filter(**where, persontrees__tree__id=tree_id).limit(20).all()


@router.get('/tree/{tree_id}/persons/{pid}')
async def person_detail(tree_id: int, pid: int, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        return await Person.objects.get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')


@router.patch('/tree/{tree_id}/persons/{pid}')
async def person_update(tree_id: int, pid: int, person: PersonSchema, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await Person.objects.filter(id=pid).update(**person.dict())
    return {'result': 'ok'}


@router.delete('/tree/{tree_id}/persons/{pid}')
async def person_delete(tree_id: int, pid: int, user: User = Security(get_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    person = await Person.objects.get_or_none(id=pid)
    await PersonTree.objects.filter(tree=tree, person=person).delete()
    if not await PersonTree.objects.filter(person=person).exists():
        await person.delete()
    return {'result': 'ok'}


@router.delete('/tree/{tree_id}/persons/{from_}/relatives/{to}')
async def person_relative_delete(tree_id: int, from_: int, to: int, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        person_from = await Person.objects.get(id=from_)
        person_to = await Person.objects.get(id=to)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')
    await person_from.remove_relative(person_to)
    return {'result': 'ok'}


@router.post('/tree/{tree_id}/relations')
async def relation_create(relation: RelationSchema, tree_id: int, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    rel = await Relation.objects.create(
        person_from=await Person.objects.get(id=relation.person_from),
        person_to=await Person.objects.get(id=relation.person_to),
        type=relation.relation,
    )
    back_rel = await Relation.objects.create(
       person_from=rel.person_to,
       person_to=rel.person_from,
       type=BACK_RELATIONS[relation.relation],
    )
    return {
        'relation': rel,
        'back_relation': back_rel,
    }
