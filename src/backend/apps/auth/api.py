from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Cookie, HTTPException, Query, Security, status
from fastapi.background import BackgroundTasks
from fastapi.responses import Response

from tools.datetime import utcnow

from ..core.models import Token, TokenActions
from ..core.utils import str_to_uuid
from .emails import email_reset_password
from .models import User
from .schemas import ChangePassword, Credentials, EmailSchema, ResetPassword, ResultOk
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
    from .emails import email_verify

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
    background_tasks.add_task(email_verify, cred.email, token)
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


@router.post('/request-password-reset', response_model=ResultOk)
async def api_request_password_reset(body: EmailSchema):
    if not (user := await User.objects.get_or_none(email=body.email)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    dt = utcnow()
    token = await Token.objects.get_or_none(user=user, action=TokenActions.RESET_PASSWORD, valid_until__gt=dt)
    if not token:
        await Token.objects.filter(user=user, action=TokenActions.RESET_PASSWORD, valid_until__lt=dt).delete()
        dt = dt + timedelta(hours=1)
        token = await Token.objects.create(user=user, action=TokenActions.RESET_PASSWORD, valid_until=dt)
    await email_reset_password(body.email, str(token.token))
    return {'result': 'ok'}


@router.post('/reset-password', response_model=ResultOk)
async def api_reset_password(body: ResetPassword):
    if not (token := await Token.objects.get_or_none(token=str_to_uuid(body.token))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    await User.objects.filter(id=token.user.id).update(password=hash_password(body.password))
    await token.delete()
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
