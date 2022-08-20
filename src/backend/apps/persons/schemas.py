from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .constants import Gender, RelationType


class PersonSchema(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    gender: Gender
    birthdate: Optional[datetime] = None
    birthplace: Optional[str] = None
    info: Optional[str] = None


class RelationSchema(BaseModel):
    person_from: int
    person_to: int
    relation: RelationType
