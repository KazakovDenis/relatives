from fastapi import APIRouter, HTTPException
from orm import MultipleMatches, NoMatch

from .models import Person
from .schemas import PersonSchema


router = APIRouter(prefix='/persons')


@router.get('/')
async def person_list():
    return await Person.objects.all()


@router.post('/')
async def person_create(person: PersonSchema):
    return await Person.objects.create(**person.dict())


@router.get('/{pid}')
async def person_detail(pid: int):
    try:
        return await Person.objects.get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')
