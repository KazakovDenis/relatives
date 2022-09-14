from pydantic import BaseModel, EmailStr, constr


class Credentials(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
