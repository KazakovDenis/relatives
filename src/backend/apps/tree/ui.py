from deps import templates
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix='/persons')


@router.get('/add', response_class=HTMLResponse)
async def person_add(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('person_detail.html', ctx)
