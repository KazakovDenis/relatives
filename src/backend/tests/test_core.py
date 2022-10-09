import pytest
from apps.auth.utils import AUTH_COOKIE
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
async def test_core_api_not_logged(client, method, path):
    response = getattr(client, method)(CORE_PREFIX + path)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures('user')
async def test_core_api_tree_list(client, session):
    response = client.get(
        CORE_PREFIX + '/tree',
        cookies={
          AUTH_COOKIE: f'Bearer {session}',
        },
    )
    assert response.status_code == status.HTTP_200_OK
    # TODO: add schema test
    assert isinstance(response.json(), list)
