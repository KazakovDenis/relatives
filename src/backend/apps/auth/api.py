from typing import Optional

from fastapi import APIRouter, Cookie, HTTPException, Query, Security, status
from fastapi.background import BackgroundTasks
from fastapi.responses import Response

from ..core.models import Token
from ..core.utils import str_to_uuid
from .models import User
from .schemas import ChangePassword, Credentials, ResultOk
from .utils import (
    AUTH_COOKIE,
    create_session,
    create_user,
    delete_session,
    get_active_user,
    hash_password,
    validate_password,
)


router = APIRouter(prefix='/auth')


@router.post('/signup', response_model=ResultOk)
async def api_signup(
        response: Response,
        cred: Credentials,
        background_tasks: BackgroundTasks,
        token: str = Cookie(None, alias=AUTH_COOKIE),
):
    # FIXME
    from tools.notifications.email import verify_email

    if token:
        return {'result': 'already logged in'}

    try:
        user = await create_user(pwd=cred.password, email=cred.email)
    except Exception:   # noqa - no unified exception in orm
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already exists',
        )

    token = await create_session(user)
    background_tasks.add_task(verify_email, cred.email, token)
    response.status_code = status.HTTP_201_CREATED
    return {'result': 'ok'}


@router.get('/login', response_model=ResultOk)
async def api_login(
        response: Response,
        token: str = Cookie(None, alias=AUTH_COOKIE),
        email: str = Query(),
        password: str = Query(),
):
    if token:
        await Token.objects.delete(token=str_to_uuid(token))

    user = await User.objects.get_or_none(email=email)
    if not (user and user.is_active and validate_password(password, user.password)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    token = await create_session(user)
    response.set_cookie(AUTH_COOKIE, f'Bearer {token}', secure=True, httponly=True)
    return {'result': 'ok'}


@router.get('/logout', response_model=ResultOk)
async def api_logout(response: Response, auth_token: Optional[str] = Cookie(None, alias=AUTH_COOKIE)):
    response.delete_cookie(AUTH_COOKIE)
    response.status_code = status.HTTP_202_ACCEPTED
    if auth_token:
        await delete_session(auth_token.removeprefix('Bearer '))
    return {'result': 'ok'}


@router.post('/change-password', response_model=ResultOk)
async def api_change_password(body: ChangePassword, user: User = Security(get_active_user)):
    if not (
        user.is_active
        and body.user_id == user.id
        and validate_password(body.old, user.password)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await User.objects.filter(id=user.id).update(password=hash_password(body.new))
    return {'result': 'ok'}
