from datetime import date
from typing import Optional

from pydantic import BaseModel

from .constants import Gender, RelationType


class PersonSchema(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    gender: Gender
    birthname: Optional[str] = None
    birthdate: Optional[date] = None
    birthplace: Optional[str] = None
    info: Optional[str] = None


class RelationSchema(BaseModel):
    person_from: int
    person_to: int
    relation: RelationType


class TreeSchema(BaseModel):
    name: Optional[str]
