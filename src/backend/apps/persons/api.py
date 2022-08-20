from typing import Optional

from fastapi import APIRouter, HTTPException
from orm import MultipleMatches, NoMatch

from .models import Person, Relation
from .schemas import PersonSchema, RelationSchema


router = APIRouter(prefix='/p')


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
