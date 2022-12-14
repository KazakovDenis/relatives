from fastapi import APIRouter, Body, HTTPException, Query, Request, Security, status
from fastapi.background import BackgroundTasks
from fastapi.responses import Response
from ormar import MultipleMatches, NoMatch
from pydantic import EmailStr

from deps import db

from ..auth.models import User
from ..auth.utils import get_active_user
from .constants import BACK_RELATIONS, RelationType
from .emails import email_invite_to_tree
from .file import save_person_photo
from .models import Person, PersonTree, Photo, Relation, Token, Tree, UserTree
from .permissions import has_tree_perm
from .schemas import (
    PersonSchema,
    PersonUpdateSchema,
    RecipientSchema,
    RelationSchema,
    ResultOk,
    ShareTreeSchema,
    TreeBuildSchema,
    TreeSchema,
)
from .utils import copy_tree


router = APIRouter()


@router.post('/tree', response_model=Tree)
async def tree_create(response: Response, tree: TreeSchema, user: User = Security(get_active_user)):
    ut = await UserTree.objects.select_related('tree').get_or_none(user=user, tree__name=tree.name)
    if ut:
        tree_obj = ut.tree
        response.status_code = status.HTTP_409_CONFLICT
    else:
        async with db.transaction():
            tree_obj = await Tree.objects.create(**tree.dict())
            await UserTree.objects.create(user=user, tree=tree_obj, is_owner=True)
        response.status_code = status.HTTP_201_CREATED
    return tree_obj


@router.get('/tree', response_model=list[UserTree])
async def tree_list(user: User = Security(get_active_user)):
    uts = await UserTree.objects.select_related('tree').all(user=user)
    return uts


@router.get('/tree/{tid}', response_model=Tree)
async def tree_detail(tid: int, user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tid)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return tree


@router.post('/tree/{tree_id}/share', response_model=ResultOk)
async def tree_share(tree_id: int, recipient: RecipientSchema, user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not (user := await User.objects.get_or_none(email=recipient.email, is_active=True)):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
    if await UserTree.objects.filter(user__email=recipient.email, tree__id=tree_id).exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    token = await Token.objects.create()
    await email_invite_to_tree(recipient.email, user.email, tree, token.token)
    return {'result': 'ok'}


@router.get('/tree/{tree_id}/share-link', response_model=ShareTreeSchema)
async def tree_get_share_link(request: Request, tree_id: int, user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not await UserTree.objects.get_or_none(user=user, tree__id=tree_id, is_owner=True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    token, _ = await Token.objects.get_or_create(user=user, tree=tree)
    shared_with = await User.objects.filter(usertrees__is_owner=False, usertrees__tree=tree).values('email')
    return {
        'link': request.url_for('ui_tree_join_link', tree_id=tree_id, token=token.token),
        'shared_with': shared_with,
    }


@router.post('/tree/{tree_id}/revoke-access', response_model=ResultOk)
async def tree_revoke_access(tree_id: int, email: EmailStr = Body(), user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if email == user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # user__email lookup does not work with filter-delete
    ut = await UserTree.objects.get_or_none(tree=tree, user__email=email)
    if ut:
        await ut.delete()
    return {'result': 'ok'}


@router.get('/tree/{tid}/scheme', response_model=TreeBuildSchema)
async def tree_scheme(tid: int, user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tid)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    persons = await Person.objects.exclude_fields(['persontrees']).all(persontrees__tree=tree)
    rels = (
        await Relation.objects
        .exclude(type=RelationType.CHILD)
        .all(person_from__in=[p.id for p in persons])
    )
    return {
        'nodes': persons,
        'edges': list({rel for rel in rels}),
    }


@router.post('/tree/{tree_id}/copy', response_model=ResultOk)
async def tree_copy(
    tree_id: int,
    body: TreeSchema,
    background_tasks: BackgroundTasks,
    user: User = Security(get_active_user),
):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    background_tasks.add_task(copy_tree, user, tree, body.name)
    return {'result': 'ok'}


@router.post('/tree/{tree_id}/persons', response_model=Person)
async def person_create(response: Response, person: PersonSchema, tree_id: int, user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    data = person.dict()
    photos = data.pop('photos', [])
    person = await Person.objects.create(**data)
    await PersonTree.objects.create(tree=tree, person=person)

    for photo in photos:
        await save_person_photo(person, photo)
    response.status_code = status.HTTP_201_CREATED
    return person


@router.get('/tree/{tree_id}/persons', response_model=list[Person])
async def person_list(
        tree_id: int,
        q: str = Query(''),
        exclude: int = Query(0),
        user: User = Security(get_active_user),
):
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

    persons = await (
        Person.objects.exclude(id=exclude)
        .filter(**where, persontrees__tree__id=tree_id)
        .exclude_fields(['persontrees'])
        .limit(20)
        .all()
    )
    return persons


@router.get('/tree/{tree_id}/persons/{pid}', response_model=Person)
async def person_detail(tree_id: int, pid: int, user: User = Security(get_active_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        return await Person.objects.select_related('photos').get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')


@router.patch('/tree/{tree_id}/persons/{pid}', response_model=ResultOk)
async def person_update(tree_id: int, pid: int, person: PersonUpdateSchema, user: User = Security(get_active_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    data = {k: v for k, v in person.dict().items() if v is not None}
    photos = data.pop('photos', [])
    await Person.objects.filter(id=pid).update(**data)

    person = await Person.objects.get(id=pid)
    for photo in photos:
        await save_person_photo(person, photo)
    return {'result': 'ok'}


@router.delete('/tree/{tree_id}/persons/{pid}', response_model=ResultOk)
async def person_delete(tree_id: int, pid: int, user: User = Security(get_active_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    person = await Person.objects.get_or_none(id=pid)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # delete person from current tree
    await PersonTree.objects.filter(tree=tree, person=person).delete()
    # delete person totally if it was the only tree
    if not await PersonTree.objects.filter(person=person).exists():
        await Photo.objects.filter(person=person).delete()
        await person.delete()
    return {'result': 'ok'}


@router.post('/tree/{tree_id}/relations', response_model=Relation)
async def relation_create(
        response: Response,
        relation: RelationSchema,
        tree_id: int,
        user: User = Security(get_active_user),
):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    rel = await Relation.objects.create(
        person_from=await Person.objects.get(id=relation.person_from),
        person_to=await Person.objects.get(id=relation.person_to),
        type=relation.relation,
    )
    await Relation.objects.create(
       person_from=rel.person_to,
       person_to=rel.person_from,
       type=BACK_RELATIONS[relation.relation],
    )
    response.status_code = status.HTTP_201_CREATED
    return rel


@router.delete('/tree/{tree_id}/persons/{from_}/relatives/{to}', response_model=ResultOk)
async def person_relative_delete(tree_id: int, from_: int, to: int, user: User = Security(get_active_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        person_from = await Person.objects.get(id=from_)
        person_to = await Person.objects.get(id=to)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Person not found')
    await person_from.remove_relative(person_to)
    return {'result': 'ok'}


@router.delete('/tree/{tree_id}/persons/{pid}/photos/{photo_id}', response_model=ResultOk)
async def person_photo_delete(tree_id: int, pid: int, photo_id: int, user: User = Security(get_active_user)):
    if not await has_tree_perm(user.id, tree_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    photo = await Photo.objects.get_or_none(person__id=pid, id=photo_id)
    if photo:
        await photo.delete()
    return {'result': 'ok'}
