from typing import Optional

from fastapi import APIRouter, HTTPException
from orm import MultipleMatches, NoMatch

from .models import Person, Relation, Tree
from .schemas import PersonSchema, RelationSchema, TreeSchema


router = APIRouter()


@router.get('/tree')
async def tree_list():
    return await Tree.objects.all()


@router.post('/tree')
async def tree_create(tree: TreeSchema):
    tree, created = await Tree.objects.get_or_create(**tree.dict())
    return tree


@router.get('/tree/{tid}')
async def tree_detail(tid: int):
    try:
        return await Tree.objects.get(id=tid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Tree not found')


@router.get('/persons')
async def person_list():
    return await Person.objects.all()


@router.post('/persons')
async def person_create(person: PersonSchema):
    return await Person.objects.create(**person.dict())


@router.get('/persons/{pid}')
async def person_detail(pid: int):
    try:
        return await Person.objects.get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')


@router.get('/persons/{pid}/relatives')
async def person_relatives(pid: int, relation: Optional[str] = None):
    try:
        person = await Person.objects.get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')
    return await person.get_relatives(relation)


@router.get('/relations')
async def relation_list():
    return await Relation.objects.all()


@router.post('/relations')
async def relation_create(relation: RelationSchema):
    return await Relation.objects.create(**relation.dict())


@router.get('/relations/{rid}')
async def relation_detail(rid: int):
    try:
        return await Relation.objects.get(id=rid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Relation not found')
