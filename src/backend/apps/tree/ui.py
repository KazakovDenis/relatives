from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

from deps import templates


router = APIRouter(prefix='/persons')


@router.get('/add', response_class=HTMLResponse)
async def root(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('person_detail.html', ctx)
