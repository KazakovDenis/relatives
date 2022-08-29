from deps import templates
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix='/auth')


@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('login.html', ctx)
