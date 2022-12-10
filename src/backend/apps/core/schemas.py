import sys
from datetime import date
from typing import Literal, Optional, TypedDict, Union

from config import settings
from pydantic import BaseModel, EmailStr, validator

from .constants import Gender, RelationType
from .models import Person, Relation


class ResultOk(TypedDict):
    result: Literal['ok']


class PersonSchema(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    gender: Gender
    birthname: Optional[str] = None
    birthdate: Optional[Union[date, Literal['']]] = None
    birthplace: Optional[str] = None
    info: Optional[str] = None
    photos: list[str]

    # TODO: remove after fix on the front
    @validator('birthdate')
    def birthdate_str_or_date(cls, v):
        return None if v == '' else v

    @validator('photos')
    def validate_photos(cls, v):
        for photo in v:
            if sys.getsizeof(photo) > settings.MAX_FILE_SIZE:
                raise ValueError('File is too large')
        return v


class PersonUpdateSchema(PersonSchema):
    name: Optional[str]
    surname: Optional[str]
    gender: Optional[Gender]


class RelationSchema(BaseModel):
    person_from: int
    person_to: int
    relation: RelationType


class TreeSchema(BaseModel):
    name: Optional[str]


class TreeBuildSchema(BaseModel):
    nodes: list[Person]
    edges: list[Relation]


class RelationCreateSchema(BaseModel):
    relation: Relation
    back_relation: Relation


class RecipientSchema(BaseModel):
    email: EmailStr
