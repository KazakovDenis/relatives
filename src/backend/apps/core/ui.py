from deps import templates
from fastapi import APIRouter, Query, Security
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..auth.models import User
from ..auth.utils import get_user
from .models import Person, PersonTree, Relation, Tree, UserTree
from .permissions import has_tree_perm


router = APIRouter()
PERSONS_PER_PAGE = 20


@router.get('/welcome', response_class=RedirectResponse)
async def ui_welcome(request: Request, user: User = Security(get_user)):
    ut = await UserTree.objects.get_or_none(user=user)
    if not ut:
        tree = await Tree.objects.create()
        ut = await UserTree.objects.create(user=user, tree=tree)
    return RedirectResponse(request.url_for('ui_tree_list', tree_id=ut.tree.id))


@router.api_route('/tree/{tree_id}/list', methods=['GET', 'POST'], response_class=HTMLResponse)
async def ui_tree_list(request: Request, tree_id: int, page: int = Query(1), user: User = Security(get_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        return RedirectResponse(request.url_for('ui_welcome'))

    offset = (page - 1) * PERSONS_PER_PAGE

    pts = await (
        PersonTree.objects.select_related('person')
        .offset(offset)
        .limit(PERSONS_PER_PAGE)
        .all(tree=tree)
    )

    ctx = {
        'request': request,
        'tree': tree,
        'page': page,
        'offset': offset,
        'persons': [pt.person for pt in pts],
    }
    return templates.TemplateResponse('tree_list.html', ctx)


# TODO: change to DELETE for front + api
@router.get('/tree/{tree_id}/delete', response_class=HTMLResponse)
async def ui_tree_delete(request: Request, tree_id: int, user: User = Security(get_user)):
    if not (tree := await has_tree_perm(user.id, tree_id)):
        return RedirectResponse(request.url_for('ui_welcome'))

    other = (
        await UserTree.objects.select_related('tree')
        .exclude(tree__id=tree_id)
        .filter(user=user)
        .get_or_none()
    )
    if not other:
        # raise HTTPException(status_code=403, detail='Cant delete the last tree')
        return RedirectResponse(request.url_for('ui_welcome'))

    await UserTree.objects.filter(tree=tree, user=user).delete()

    # do not delete a tree if it has another related users
    if not await UserTree.objects.filter(tree=tree).exists():
        await tree.delete()

    return RedirectResponse(request.url_for('ui_tree_list', tree_id=tree_id))


@router.get('/tree/{tree_id}/scheme', response_class=HTMLResponse)
async def ui_tree_scheme(request: Request, tree_id: int, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        return RedirectResponse(request.url_for('ui_welcome'))

    tree = await Tree.objects.get(id=tree_id)
    ctx = {'request': request, 'tree': tree}
    return templates.TemplateResponse('tree_scheme.html', ctx)


@router.get('/tree/{tree_id}/person/add', response_class=HTMLResponse)
async def ui_person_add(request: Request, tree_id: int, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        return RedirectResponse(request.url_for('ui_welcome'))
    ctx = {'request': request, 'tree_id': tree_id}
    return templates.TemplateResponse('person_detail.html', ctx)


@router.get('/tree/{tree_id}/person/{person_id}', response_class=HTMLResponse)
async def ui_person_detail(request: Request, tree_id: int, person_id: int, user: User = Security(get_user)):
    if not await has_tree_perm(user.id, tree_id):
        return RedirectResponse(request.url_for('ui_welcome'))

    person = await Person.objects.get(id=person_id)
    relations = await Relation.objects.select_related('person_to').order_by('type').all(person_from=person)

    ctx = {
        'request': request,
        'tree_id': tree_id,
        'person': person,
        'relations': relations,
    }
    return templates.TemplateResponse('person_detail.html', ctx)
