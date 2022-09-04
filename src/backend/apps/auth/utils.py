import uuid
from datetime import datetime
from hashlib import sha256
from typing import Optional

from .models import Session, User


AUTH_COOKIE = 'Authorization'


def hash_password(pwd: str) -> str:
    return sha256(pwd.encode()).hexdigest()


def validate_password(rcv_pwd: str, ex_pwd: str) -> bool:
    return hash_password(rcv_pwd) == ex_pwd


async def create_user(pwd: str, **kwargs) -> User:
    hashed = hash_password(pwd)
    user = await User.objects.create(password=hashed, **kwargs)
    return user


async def create_session(user: User) -> str:
    token = str(uuid.uuid4())
    await Session.objects.create(
        user=user,
        token=token,
        issued_at=datetime.utcnow(),
    )
    return token


def token_to_uuid(token: str) -> Optional[uuid.UUID]:
    try:
        return uuid.UUID(token)
    except (AttributeError, TypeError, ValueError):
        return None


async def delete_session(token: str):
    if as_uuid := token_to_uuid(token):
        await Session.objects.filter(token=as_uuid).delete()