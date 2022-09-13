from apps.core.models import Person, PersonTree, Relation, Tree, UserTree
from deps import templates
from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse


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


@router.get('/welcome', response_class=HTMLResponse)
async def ui_welcome(request: Request):
    ut = await UserTree.objects.first(user=request.user.user)
    if not ut:
        tree = await Tree.objects.create()
        ut = await UserTree.objects.create(user=request.user.user, tree=tree)
    return RedirectResponse(request.url_for('ui_tree_list', tree_id=ut.tree.id))


@router.api_route('/tree/{tree_id}/list', methods=['GET', 'POST'], response_class=HTMLResponse)
async def ui_tree_list(request: Request, tree_id: int, page: int = Query(1)):
    ut = await UserTree.objects.select_related('tree').first(user=request.user.user, tree__id=tree_id)
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
    ut = await UserTree.objects.exclude(tree__id=tree_id).filter(user=request.user.user).first()
    if not ut:
        # raise HTTPException(status_code=403, detail='Cant delete the last tree')
        return RedirectResponse(request.url_for('ui_tree_list', tree_id=tree_id))

    await Tree.objects.filter(id=tree_id).delete()
    return RedirectResponse(request.url_for('ui_tree_list', tree_id=ut.tree.id))


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
