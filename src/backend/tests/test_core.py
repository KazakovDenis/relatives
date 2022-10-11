import pytest
from apps.auth.utils import AUTH_COOKIE
from apps.core.models import Person, Tree
from apps.core.schemas import TreeBuildSchema
from fastapi import status


CORE_PREFIX = '/api/v1'


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
def test_core_api_not_logged(client, method, path):
    response = getattr(client, method)(CORE_PREFIX + path)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_core_api_tree_create(async_teardown, client, session):
    name = 'Test'
    async_teardown(Tree.objects.delete(name=name))

    response = client.post(
        CORE_PREFIX + '/tree',
        json={'name': name},
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Tree(**response.json())


def test_core_api_tree_list(client, session, tree):
    response = client.get(
        CORE_PREFIX + '/tree',
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert Tree(**response.json()[0])


def test_core_api_tree_detail(client, session, tree):
    response = client.get(
        CORE_PREFIX + f'/tree/{tree.id}',
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert Tree(**response.json())


def test_core_api_tree_scheme(client, session, tree):
    response = client.get(
        CORE_PREFIX + f'/tree/{tree.id}/scheme',
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert TreeBuildSchema(**response.json())


def test_core_api_tree_person_list(client, session, tree, person):
    response = client.get(
        CORE_PREFIX + f'/tree/{tree.id}/persons?q={person.surname}',
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert Person(**response.json()[0])


def test_core_api_tree_person_detail(client, session, tree, person):
    response = client.get(
        CORE_PREFIX + f'/tree/{tree.id}/persons/{person.id}',
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert Person(**response.json())
