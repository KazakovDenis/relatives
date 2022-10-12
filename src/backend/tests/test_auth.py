import pytest
from apps.auth.models import User
from apps.auth.utils import AUTH_COOKIE
from fastapi import status
from tests import settings


AUTH_PREFIX = '/api/v1/auth'


@pytest.mark.parametrize('path', [
    '/',
    '/ui/login',
    '/ui/signup',
])
def test_auth_ui_pages(client, path):
    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK


def test_auth_api_signup(async_teardown, client):
    email = 'signup@test.com'
    async_teardown(User.objects.delete(email=email))

    response = client.post(
        AUTH_PREFIX + '/signup',
        json={
            'email': email,
            'password': 'test:user',
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.usefixtures('user', 'blocked_user')
@pytest.mark.parametrize('email, pwd, status_code', [
    (settings.ACTIVE_USER_EMAIL, settings.ACTIVE_USER_PASS, status.HTTP_200_OK),
    (settings.BLOCKED_USER_EMAIL, settings.BLOCKED_USER_PASS, status.HTTP_403_FORBIDDEN),
    ('unknown@test.com', 'test:unknown', status.HTTP_403_FORBIDDEN),
])
def test_auth_api_login(client, email, pwd, status_code):
    response = client.get(
        AUTH_PREFIX + '/login',
        params={
            'email': email,
            'password': pwd,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize('logged_in', [True, False])
def test_auth_api_logout(client, user, logged_in, session):
    token = session if logged_in else ''
    response = client.get(
        AUTH_PREFIX + '/logout',
        cookies={
            AUTH_COOKIE: f'Bearer {token}',
        },
    )
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.parametrize('cookie', ['Basic login:pass', 'Bearer not_uuid'])
def test_auth_bad_auth_cookie(client, user, cookie):
    response = client.get('/api/v1/tree', cookies={AUTH_COOKIE: cookie})
    assert response.status_code == status.HTTP_403_FORBIDDEN