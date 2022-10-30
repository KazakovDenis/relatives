from deps import templates
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .models import Session, User
from .utils import AUTH_COOKIE, create_session, token_to_uuid


router = APIRouter()


@router.get('/signup', response_class=HTMLResponse)
async def ui_signup(request: Request):
    ctx = {'request': request, 'public': True, 'signup': True}
    return templates.TemplateResponse('login.html', ctx)


@router.get('/login', response_class=HTMLResponse)
async def ui_login(request: Request):
    ctx = {'request': request, 'public': True}
    return templates.TemplateResponse('login.html', ctx)


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
    ctx = {'request': request, 'public': True}
    return templates.TemplateResponse('verify_email.html', ctx)
