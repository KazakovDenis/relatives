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


@router.api_route('/tree/list', methods=['GET', 'POST'], response_class=HTMLResponse)
async def ui_tree_list(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('tree_list.html', ctx)


@router.get('/tree/scheme', response_class=HTMLResponse)
async def ui_tree_scheme(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('tree_scheme.html', ctx)


@router.get('/person', response_class=HTMLResponse)
async def ui_person_detail(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('person_detail.html', ctx)
