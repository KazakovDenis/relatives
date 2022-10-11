from datetime import date
from typing import Literal, Optional, TypedDict, Union

from pydantic import BaseModel, validator

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

    # TODO: remove after fix on the front
    @validator('birthdate')
    def birthdate_str_or_date(cls, v):
        return None if v == '' else v


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
