from deps import templates
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()


@router.get('/login', response_class=HTMLResponse)
async def ui_login(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('login.html', ctx)


@router.post('/login', response_class=HTMLResponse)
async def ui_login(request: Request):   # noqa: F811
    return RedirectResponse(request.url_for('ui_tree_list'))


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
