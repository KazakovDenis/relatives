import pytest
from fastapi import status

from apps.auth.utils import AUTH_COOKIE
from apps.core.constants import Gender
from apps.core.models import Person, PersonTree, Relation, Token, Tree, UserTree
from apps.core.schemas import RelationType, ResultOk, TreeBuildSchema

from . import constants


CORE_API_PREFIX = '/api/v1'


def build_path(path, tree_id, person_id, relative_id) -> str:
    match path.count('%s'):
        case 1:
            path = path % tree_id
        case 2:
            path = path % (tree_id, person_id)
        case 3:
            path = path % (tree_id, person_id, relative_id)
    return path


@pytest.fixture
def api_request(async_client, session):
    def inner(method, path, auth, **kwargs):
        if auth:
            kwargs['cookies'] = {AUTH_COOKIE: f'Bearer {session}'}
        return getattr(async_client, method)(CORE_API_PREFIX + path, **kwargs)
    return inner


@pytest.mark.usefixtures('tree', 'person')
@pytest.mark.parametrize('path', [
    '/tree',
    '/tree/%s',
    '/tree/%s/scheme',
    '/tree/%s/copy',
    '/tree/%s/persons',
    '/tree/%s/persons/%s',
    '/tree/%s/persons/%s/relatives/%s',
    '/tree/%s/relations',
    '/tree/%s/share',
    '/tree/%s/share-link',
    '/tree/%s/revoke-access',
])
async def test_core_api_not_logged(api_request, tree, person, relative, path):
    path = build_path(path, tree.id, person.id, relative.id)
    response = await api_request('get', path, auth=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# TODO: permission tests for other HTTP-method endpoints
@pytest.mark.parametrize('path', [
    '/tree/%s',
    '/tree/%s/scheme',
    '/tree/%s/persons',
    '/tree/%s/persons/%s',
])
async def test_core_api_tree_user_denied(async_teardown, api_request, person, relative, path):
    tree = await Tree.objects.create(name='denied')
    async_teardown(tree.delete())

    path = build_path(path, tree.id, person.id, relative.id)
    response = await api_request('get', path, auth=True)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize('exists, status_code', [
    (False, status.HTTP_201_CREATED),
    (True, status.HTTP_409_CONFLICT),
])
async def test_core_api_tree_create(async_teardown, api_request, tree, exists, status_code):
    name = tree.name if exists else 'New test'
    async_teardown(Tree.objects.delete(name=name))

    response = await api_request('post', '/tree', auth=True, json={'name': name})
    assert response.status_code == status_code
    assert Tree(**response.json())


@pytest.mark.usefixtures('tree')
async def test_core_api_tree_list(api_request):
    response = await api_request('get', '/tree', auth=True)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()[0]
    data['tree'] = data['tree']['id']
    assert UserTree(**data)


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
async def test_core_api_tree_detail(api_request, tree, exists, status_code):
    response = await api_request('get', f'/tree/{tree.id if exists else 0}', auth=True)
    assert response.status_code == status_code
    if exists:
        assert Tree(**response.json())


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
async def test_core_api_tree_scheme(api_request, tree, exists, status_code):
    response = await api_request('get', f'/tree/{tree.id if exists else 0}/scheme', auth=True)
    assert response.status_code == status_code
    if exists:
        assert TreeBuildSchema(**response.json())


async def test_core_api_tree_person_create(async_teardown, api_request, tree):
    person_data = {
        'name': 'Name',
        'surname': 'Surname',
        'gender': Gender.MALE.value,
    }
    async_teardown(Person.objects.delete(**person_data))

    response = await api_request('post', f'/tree/{tree.id}/persons', auth=True, json=person_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Person(**response.json())


@pytest.mark.usefixtures('person')
@pytest.mark.parametrize('fullname', ['Doe', 'Doe John'])
async def test_core_api_tree_person_list_ok(api_request, tree, fullname):
    response = await api_request('get', f'/tree/{tree.id}/persons?q={fullname}', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert Person(**response.json()[0])


async def test_core_api_tree_person_list_unknown(api_request, tree):
    response = await api_request('get', f'/tree/{tree.id}/persons?q=unknown', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_404_NOT_FOUND),
])
async def test_core_api_tree_person_detail(api_request, tree, person, exists, status_code):
    response = await api_request('get', f'/tree/{tree.id}/persons/{person.id if exists else 0}', auth=True)
    assert response.status_code == status_code
    if exists:
        assert Person(**response.json())


async def test_core_api_tree_person_update(api_request, tree, person):
    person_data = {'info': 'Update person'}
    assert person.info != person_data['info']

    response = await api_request('patch', f'/tree/{tree.id}/persons/{person.id}', auth=True, json=person_data)
    assert response.status_code == status.HTTP_200_OK
    assert ResultOk(**response.json())

    await person.load()
    assert person.info == person_data['info']


async def test_core_api_tree_person_delete_totally(api_request, tree, person):
    response = await api_request('delete', f'/tree/{tree.id}/persons/{person.id}', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert ResultOk(**response.json())
    assert not await Person.objects.all(id=person.id)


async def test_core_api_tree_person_delete_from_tree(async_teardown, api_request, tree, person):
    new_tree = await Tree.objects.create(name='Delete person')
    await PersonTree.objects.create(person=person, tree=new_tree)
    async_teardown(new_tree.delete())

    response = await api_request('delete', f'/tree/{tree.id}/persons/{person.id}', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert ResultOk(**response.json())
    assert await Person.objects.all(id=person.id)


async def test_core_api_tree_relative_add(api_request, tree, person, relative):
    relation = {
        'person_from': person.id,
        'person_to': relative.id,
        'relation': RelationType.SPOUSE.value,
    }
    response = await api_request('post', f'/tree/{tree.id}/relations', auth=True, json=relation)
    assert response.status_code == status.HTTP_201_CREATED

    # TODO: should endpoint return the whole object or only id?
    data = response.json()
    data['person_to'] = data['person_to']['id']
    data['person_from'] = data['person_from']['id']
    assert Relation(**data)


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_404_NOT_FOUND),
])
async def test_core_api_tree_relative_delete(api_request, tree, person, relative, exists, status_code):
    await person.add_relative(RelationType.SPOUSE, relative)
    to = relative.id if exists else 0
    response = await api_request('delete', f'/tree/{tree.id}/persons/{person.id}/relatives/{to}', auth=True)
    assert response.status_code == status_code
    if exists:
        assert ResultOk(**response.json())


async def test_core_api_tree_revoke_access_from_self(api_request, user, tree):
    response = await api_request('post', f'/tree/{tree.id}/revoke-access', auth=True, json=user.email)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_core_api_tree_revoke_access_another_tree(api_request):
    response = await api_request('post', '/tree/0/revoke-access', auth=True, json='test@email.com')
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_core_api_tree_revoke_access_ok(api_request, tree):
    response = await api_request('post', f'/tree/{tree.id}/revoke-access', auth=True, json='test@email.com')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures('super_user')
async def test_core_api_tree_share_ok(api_request, tree):
    body = {'email': constants.SUPER_USER_EMAIL}
    response = await api_request('post', f'/tree/{tree.id}/share', auth=True, json=body)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures('super_user')
@pytest.mark.parametrize('has_tree,email,result', [
    (False, constants.SUPER_USER_EMAIL, status.HTTP_403_FORBIDDEN),
    (True, constants.INACTIVE_USER_EMAIL, status.HTTP_406_NOT_ACCEPTABLE),
    (True, constants.ACTIVE_USER_EMAIL, status.HTTP_409_CONFLICT),
])
async def test_core_api_tree_share_fail(api_request, tree, user, has_tree, email, result):
    tree_id = tree.id if has_tree else 0
    body = {'email': email}
    response = await api_request('post', f'/tree/{tree_id}/share', auth=True, json=body)
    assert response.status_code == result


# UI tests
@pytest.fixture
def ui_request(async_client, session):
    def inner(method, path, auth, **kwargs):
        if auth:
            kwargs['cookies'] = {AUTH_COOKIE: f'Bearer {session}'}
        return getattr(async_client, method)('/ui' + path, **kwargs)
    return inner


@pytest.mark.parametrize('path, status_code', [
    ('/welcome', status.HTTP_307_TEMPORARY_REDIRECT),
    ('/tree/%s/list', status.HTTP_200_OK),
    ('/tree/%s/scheme', status.HTTP_200_OK),
    ('/tree/%s/person/add', status.HTTP_200_OK),
    ('/tree/%s/person/%s', status.HTTP_200_OK),
])
async def test_core_ui_ok(ui_request, path, status_code, tree, person):
    path = build_path(path, tree.id, person.id, None)
    response = await ui_request('get', path, auth=True, follow_redirects=False)
    assert response.status_code == status_code


@pytest.mark.parametrize('path', [
    '/tree/%s/list',
    '/tree/%s/delete',
    '/tree/%s/scheme',
    '/tree/%s/person/add',
    '/tree/%s/person/%s',
])
async def test_core_ui_tree_user_denied(async_teardown, ui_request, person, path):
    tree = await Tree.objects.create(name='denied')
    async_teardown(tree.delete())

    path = build_path(path, tree.id, person.id, None)
    response = await ui_request('get', path, auth=True, follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


async def test_core_ui_last_tree_not_deleted(ui_request, tree):
    response = await ui_request('get', f'/tree/{tree.id}/delete', auth=True, follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert await Tree.objects.all(id=tree.id)


async def test_core_ui_tree_delete(async_teardown, ui_request, user, tree):
    new_tree = await Tree.objects.create(name='one more tree')
    await UserTree.objects.create(tree=new_tree, user=user)
    async_teardown(new_tree.delete())

    response = await ui_request('get', f'/tree/{tree.id}/delete', auth=True, follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert not await Tree.objects.all(id=tree.id)


@pytest.mark.parametrize('auth', [True, False])
@pytest.mark.parametrize('real_tree', [True, False])
@pytest.mark.parametrize('has_token', [True, False])
@pytest.mark.parametrize('email', ['', 'unknown@email.com', constants.ACTIVE_USER_EMAIL])
async def test_core_ui_tree_join_forbidden(ui_request, tree, email, has_token, real_tree, auth):
    token = (await Token.objects.create()).token if has_token else ''
    tree_id = tree.id if real_tree else 0

    assert await UserTree.objects.filter(tree=tree).count() == 1
    response = await ui_request(
        'get',
        f'/tree/{tree_id}/join?email={email}&token={token}',
        auth=auth,
        follow_redirects=False,
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert await UserTree.objects.filter(tree=tree).count() == 1


async def test_core_ui_tree_join_ok(ui_request, tree, user):
    token = (await Token.objects.create()).token
    response = await ui_request(
        'get',
        f'/tree/{tree.id}/join?email={constants.ACTIVE_USER_EMAIL}&token={token}',
        auth=True,
        follow_redirects=False,
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    ut = await UserTree.objects.get_or_none(user=user, tree=tree)
    assert ut
    assert not ut.is_owner
