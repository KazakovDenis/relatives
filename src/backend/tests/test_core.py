import pytest
from apps.auth.utils import AUTH_COOKIE
from apps.core.models import Tree, UserTree
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


async def test_core_api_tree_list(request, event_loop, client, user, session):
    tree = await Tree.objects.create(name='Test')
    await UserTree.objects.create(tree=tree, user=user)
    request.addfinalizer(lambda: event_loop.run_until_complete(tree.delete()))

    response = client.get(
        CORE_PREFIX + '/tree',
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert Tree(**response.json()[0])


def test_core_api_tree_create(request, event_loop, client, session):
    name = 'Test'

    async def teardown():
        await Tree.objects.delete(name=name)
    request.addfinalizer(lambda: event_loop.run_until_complete(teardown()))

    response = client.post(
        CORE_PREFIX + '/tree',
        json={'name': name},
        cookies={AUTH_COOKIE: f'Bearer {session}'},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Tree(**response.json())
