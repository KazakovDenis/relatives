from fastapi import APIRouter, HTTPException, Query, Security, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from deps import templates

from .models import Session, User
from .utils import AUTH_COOKIE, create_session, get_active_user, token_to_uuid


router = APIRouter()


@router.get('/signup', response_class=HTMLResponse)
async def ui_signup(request: Request):
    ctx = {'request': request, 'public': True, 'signup': True}
    return templates.TemplateResponse('public/login.html', ctx)


@router.get('/login', response_class=HTMLResponse)
async def ui_login(request: Request):
    ctx = {'request': request, 'public': True}
    return templates.TemplateResponse('public/login.html', ctx)


@router.get('/activate', response_class=RedirectResponse)
async def ui_activate(request: Request, token: str | None = Query(None)):
    session = await Session.objects.get_or_none(token=token_to_uuid(token))
    if not session:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # recreate to avoid activation of blocked users
    new_token = await create_session(session.user)

    await User.objects.filter(id=session.user.id).update(is_active=True)
    response = RedirectResponse(request.url_for('ui_welcome'))
    response.set_cookie(AUTH_COOKIE, f'Bearer {new_token}', secure=True, httponly=True)
    await session.delete()
    return response


@router.get('/verify-email', response_class=HTMLResponse)
async def ui_verify_email(request: Request):
    ctx = {'request': request, 'public': True, 'text': 'Please, check your email to continue'}
    return templates.TemplateResponse('public/empty.html', ctx)


@router.get('/forbidden', response_class=HTMLResponse)
async def ui_forbidden(request: Request):
    ctx = {'request': request, 'public': True, 'text': 'Forbidden'}
    return templates.TemplateResponse('public/empty.html', ctx)


@router.get('/profile/{user_id}/password', response_class=HTMLResponse)
async def ui_change_password(request: Request, user_id: int, user: User = Security(get_active_user)):
    if user_id != user.id:
        return RedirectResponse(request.url_for('ui_forbidden'))

    ctx = {
        'request': request,
        'user': user,
    }
    return templates.TemplateResponse('password.html', ctx)
