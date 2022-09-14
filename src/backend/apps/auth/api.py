from typing import Optional

from fastapi import APIRouter, Cookie, HTTPException, Query, status
from fastapi.responses import Response

from .models import User
from .schemas import Credentials
from .utils import AUTH_COOKIE, create_session, create_user, delete_session, validate_password


router = APIRouter(prefix='/auth')


@router.post('/signup')
async def api_signup(
        response: Response,
        cred: Credentials,
        token: str = Cookie(None, alias=AUTH_COOKIE),
):
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
    response.set_cookie(AUTH_COOKIE, f'Bearer {token}', secure=True, httponly=True)
    return {'result': 'ok'}


@router.get('/login')
async def api_login(
        response: Response,
        token: str = Cookie(None, alias=AUTH_COOKIE),
        email: str = Query(),
        password: str = Query(),
):
    if token:
        return {'result': 'already logged in'}

    user = await User.objects.first(email=email)
    if not (user and validate_password(password, user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
        )
    token = await create_session(user)
    response.set_cookie(AUTH_COOKIE, f'Bearer {token}', secure=True, httponly=True)
    return {'result': 'ok'}


@router.get('/logout')
async def api_logout(response: Response, auth_token: Optional[str] = Cookie(None, alias=AUTH_COOKIE)):
    response.delete_cookie(AUTH_COOKIE)
    if auth_token:
        await delete_session(auth_token.removeprefix('Bearer '))
    return {'result': 'ok'}
