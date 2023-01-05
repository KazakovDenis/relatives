from typing import Literal, TypedDict

from pydantic import BaseModel, EmailStr, constr


class EmailSchema(BaseModel):
    email: EmailStr


class Credentials(EmailSchema):
    password: constr(min_length=6)


class ResultOk(TypedDict):
    result: Literal['ok']


class ResetPassword(BaseModel):
    token: str
    password: str


class ChangePassword(BaseModel):
    user_id: int
    old: str
    new: str
