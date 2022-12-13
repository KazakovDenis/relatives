import pytest
from apps.auth.models import Session, User
from apps.auth.utils import AUTH_COOKIE, create_session, token_to_uuid
from fastapi import status
from tests import constants


AUTH_PREFIX = '/api/v1/auth'


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


@pytest.mark.usefixtures('user', 'inactive_user')
@pytest.mark.parametrize('email, pwd, status_code', [
    (constants.ACTIVE_USER_EMAIL, constants.ACTIVE_USER_PASS, status.HTTP_200_OK),
    (constants.INACTIVE_USER_EMAIL, constants.INACTIVE_USER_PASS, status.HTTP_403_FORBIDDEN),
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


# UI tests
@pytest.mark.parametrize('path', [
    '/',
    '/ui/login',
    '/ui/signup',
    '/ui/verify-email',
])
def test_auth_ui_pages(client, path):
    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK


def test_auth_ui_activate_forbidden(client):
    response = client.get('/ui/activate')
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_auth_ui_activate_ok(client, inactive_user):
    session = await create_session(inactive_user)

    response = client.get(f'/ui/activate?token={session}', allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    await inactive_user.load()
    assert inactive_user.is_active
    assert not await Session.objects.all(token=token_to_uuid(session))
