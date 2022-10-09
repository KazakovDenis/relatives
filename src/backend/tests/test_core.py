import pytest
from apps.auth.utils import AUTH_COOKIE
from fastapi import status


CORE_PREFIX = '/api/v1'


@pytest.mark.usefixtures('user')
@pytest.mark.parametrize('logged_in, status_code', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
async def test_core_api_tree_list(client, session, logged_in, status_code):
    token = session if logged_in else ''
    response = client.get(
        CORE_PREFIX + '/tree',
        cookies={
          AUTH_COOKIE: f'Bearer {token}',
        },
    )
    assert response.status_code == status_code
