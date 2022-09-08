from apps.core.models import Person, PersonTree, Relation, Tree, UserTree
from deps import templates
from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse


router = APIRouter()
PERSONS_PER_PAGE = 20


@router.get('/signup', response_class=HTMLResponse)
async def ui_signup(request: Request):
    ctx = {'request': request, 'signup': True}
    return templates.TemplateResponse('login.html', ctx)


@router.get('/login', response_class=HTMLResponse)
async def ui_login(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('login.html', ctx)


# TODO: move list retrieve & rendering to JS
@router.api_route('/tree/list', methods=['GET', 'POST'], response_class=HTMLResponse)
async def ui_tree_list(request: Request, page: int = Query(1)):
    uts = await UserTree.objects.select_related('tree').all(user=request.user.user)
    if not uts:
        tree = await Tree.objects.create()
        ut = await UserTree.objects.create(user=request.user.user, tree=tree)
        uts = [ut]

    offset = (page - 1) * PERSONS_PER_PAGE

    # TODO: fetch active tree
    pts = await (
        PersonTree.objects.select_related('person')
        .offset(offset)
        .limit(PERSONS_PER_PAGE)
        .all(tree=uts[0].tree)
    )

    ctx = {
        'request': request,
        'page': page,
        'offset': offset,
        'trees': [ut.tree for ut in uts],
        'persons': [pt.person for pt in pts],
    }
    return templates.TemplateResponse('tree_list.html', ctx)


@router.get('/tree/{tree_id}/scheme', response_class=HTMLResponse)
async def ui_tree_scheme(request: Request, tree_id: int):
    ctx = {'request': request, 'tree_id': tree_id}
    return templates.TemplateResponse('tree_scheme.html', ctx)


@router.get('/person/add', response_class=HTMLResponse)
async def ui_person_add(request: Request):
    ctx = {'request': request}
    return templates.TemplateResponse('person_detail.html', ctx)


@router.get('/person/{person_id}', response_class=HTMLResponse)
async def ui_person_detail(request: Request, person_id: int):
    person = await Person.objects.get(id=person_id)
    relations = await Relation.objects.order_by('type').all(person_from=person)

    # TODO: select_related error: Please specify the 'onclause' of this join explicitly.
    for rel in relations:
        await rel.person_to.load()

    ctx = {
        'request': request,
        'person': person,
        'relations': relations,
    }
    return templates.TemplateResponse('person_detail.html', ctx)
