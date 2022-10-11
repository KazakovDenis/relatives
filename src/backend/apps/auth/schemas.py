from typing import Literal, TypedDict

from pydantic import BaseModel, EmailStr, constr


class Credentials(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class ResultOk(TypedDict):
    result: Literal['ok']
