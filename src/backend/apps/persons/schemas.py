from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PersonSchema(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    birthdate: Optional[datetime] = None
    birthplace: Optional[str] = None
    info: Optional[str] = None
    father: Optional[int] = None
    mother: Optional[int] = None
