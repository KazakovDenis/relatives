from fastapi import APIRouter

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
    return await Person.objects.get(id=pid)
