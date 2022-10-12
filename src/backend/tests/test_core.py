import pytest
from apps.auth.utils import AUTH_COOKIE
from apps.core.constants import Gender
from apps.core.models import Person, PersonTree, Tree
from apps.core.schemas import RelationType, ResultOk, TreeBuildSchema
from fastapi import status


CORE_PREFIX = '/api/v1'


@pytest.fixture
def http_request(client, session):
    def inner(method, path, auth, **kwargs):
        if auth:
            kwargs['cookies'] = {AUTH_COOKIE: f'Bearer {session}'}
        return getattr(client, method)(CORE_PREFIX + path, **kwargs)
    return inner


# TODO: add tree permission tests
@pytest.mark.usefixtures('tree', 'person')
@pytest.mark.parametrize('path', [
    '/tree',
    '/tree/1',
    '/tree/1/scheme',
    '/tree/1/persons',
    '/tree/1/persons/1',
    '/tree/1/persons/1/relatives/2',
    '/tree/1/relations',
])
@pytest.mark.parametrize('method', ['get', 'post'])
def test_core_api_not_logged(http_request, method, path):
    response = http_request(method, path, auth=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize('exists, status_code', [
    (False, status.HTTP_201_CREATED),
    (True, status.HTTP_409_CONFLICT),
])
def test_core_api_tree_create(async_teardown, http_request, tree, exists, status_code):
    name = tree.name if exists else 'New test'
    async_teardown(Tree.objects.delete(name=name))

    response = http_request('post', '/tree', auth=True, json={'name': name})
    assert response.status_code == status_code
    assert Tree(**response.json())


@pytest.mark.usefixtures('tree')
def test_core_api_tree_list(http_request):
    response = http_request('get', '/tree', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert Tree(**response.json()[0])


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
def test_core_api_tree_detail(http_request, tree, exists, status_code):
    response = http_request('get', f'/tree/{tree.id if exists else 0}', auth=True)
    assert response.status_code == status_code
    if exists:
        assert Tree(**response.json())


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
def test_core_api_tree_scheme(http_request, tree, exists, status_code):
    response = http_request('get', f'/tree/{tree.id if exists else 0}/scheme', auth=True)
    assert response.status_code == status_code
    if exists:
        assert TreeBuildSchema(**response.json())


def test_core_api_tree_person_create(async_teardown, http_request, tree):
    person_data = {
        'name': 'Name',
        'surname': 'Surname',
        'gender': Gender.MALE.value,
    }
    async_teardown(Person.objects.delete(**person_data))

    response = http_request('post', f'/tree/{tree.id}/persons', auth=True, json=person_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Person(**response.json())


@pytest.mark.usefixtures('person')
@pytest.mark.parametrize('fullname', ['Doe', 'Doe John'])
def test_core_api_tree_person_list_ok(http_request, tree, fullname):
    response = http_request('get', f'/tree/{tree.id}/persons?q={fullname}', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert Person(**response.json()[0])


def test_core_api_tree_person_list_unknown(http_request, tree):
    response = http_request('get', f'/tree/{tree.id}/persons?q=unknown', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_404_NOT_FOUND),
])
def test_core_api_tree_person_detail(http_request, tree, person, exists, status_code):
    response = http_request('get', f'/tree/{tree.id}/persons/{person.id if exists else 0}', auth=True)
    assert response.status_code == status_code
    if exists:
        assert Person(**response.json())


async def test_core_api_tree_person_update(http_request, tree, person):
    person_data = {'info': 'Update person'}
    assert person.info != person_data['info']

    response = http_request('patch', f'/tree/{tree.id}/persons/{person.id}', auth=True, json=person_data)
    assert response.status_code == status.HTTP_200_OK
    assert ResultOk(**response.json())

    await person.load()
    assert person.info == person_data['info']


async def test_core_api_tree_person_delete_totally(http_request, tree, person):
    response = http_request('delete', f'/tree/{tree.id}/persons/{person.id}', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert ResultOk(**response.json())
    assert not await Person.objects.all(id=person.id)


async def test_core_api_tree_person_delete_from_tree(async_teardown, http_request, tree, person):
    new_tree = await Tree.objects.create(name='Delete person')
    await PersonTree.objects.create(person=person, tree=new_tree)
    async_teardown(new_tree.delete())

    response = http_request('delete', f'/tree/{tree.id}/persons/{person.id}', auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert ResultOk(**response.json())
    assert await Person.objects.all(id=person.id)


async def test_core_api_tree_relative_add(http_request, tree, person, relative):
    relation = {
        'person_from': person.id,
        'person_to': relative.id,
        'relation': RelationType.SPOUSE.value,
    }
    response = http_request('post', f'/tree/{tree.id}/relations', auth=True, json=relation)
    assert response.status_code == status.HTTP_201_CREATED
    # TODO: validate schema
    assert response.json()


@pytest.mark.parametrize('exists, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_404_NOT_FOUND),
])
async def test_core_api_tree_relative_delete(http_request, tree, person, relative, exists, status_code):
    await person.add_relative(RelationType.SPOUSE, relative)
    to = relative.id if exists else 0
    response = http_request('delete', f'/tree/{tree.id}/persons/{person.id}/relatives/{to}', auth=True)
    assert response.status_code == status_code
    if exists:
        assert ResultOk(**response.json())
