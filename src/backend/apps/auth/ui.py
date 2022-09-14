from deps import templates
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get('/signup', response_class=HTMLResponse)
async def ui_signup(request: Request):
    ctx = {'request': request, 'signup': True}
    return templates.TemplateResponse('login.html', ctx)


@router.get('/login', response_class=HTMLResponse)
async def ui_login(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('login.html', ctx)
