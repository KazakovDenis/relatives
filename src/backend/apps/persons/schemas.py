from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .constants import Gender


class PersonSchema(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    gender: Gender
    birthdate: Optional[datetime] = None
    birthplace: Optional[str] = None
    info: Optional[str] = None
