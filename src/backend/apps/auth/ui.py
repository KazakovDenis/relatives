from apps.core.models import Person, PersonTree, Relation, Tree, UserTree
from deps import templates
from fastapi import APIRouter, HTTPException, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from orm import MultipleMatches, NoMatch


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


@router.api_route('/tree/{tree_id}/list', methods=['GET', 'POST'], response_class=HTMLResponse)
async def ui_tree_list(request: Request, tree_id: int, page: int = Query(1)):
    ut = await UserTree.objects.select_related('tree').first(user=request.user.user, tree__id=tree_id)
    if not ut:
        tree = await Tree.objects.create()
        ut = await UserTree.objects.create(user=request.user.user, tree=tree)

    offset = (page - 1) * PERSONS_PER_PAGE

    pts = await (
        PersonTree.objects.select_related('person')
        .offset(offset)
        .limit(PERSONS_PER_PAGE)
        .all(tree=ut.tree)
    )

    ctx = {
        'request': request,
        'tree': ut.tree,
        'page': page,
        'offset': offset,
        'persons': [pt.person for pt in pts],
    }
    return templates.TemplateResponse('tree_list.html', ctx)


# TODO: change to DELETE for front + api
@router.get('/tree/{tree_id}/delete', response_class=HTMLResponse)
async def ui_tree_delete(request: Request, tree_id: int):
    try:
        this_tree = await Tree.objects.get(id=tree_id)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Tree not found')

    next_tree = await Tree.objects.exclude(id=tree_id).first()
    if not next_tree:
        raise HTTPException(status_code=403, detail='Cant delete the last tree')

    await this_tree.delete()
    return RedirectResponse(request.url_for('ui_tree_list', tree_id=next_tree.id))


@router.get('/tree/{tree_id}/scheme', response_class=HTMLResponse)
async def ui_tree_scheme(request: Request, tree_id: int):
    tree = await Tree.objects.get(id=tree_id)
    ctx = {'request': request, 'tree': tree}
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
