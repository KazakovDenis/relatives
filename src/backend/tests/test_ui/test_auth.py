import pytest


@pytest.mark.parametrize('path', [
    '/',
    '/ui/login',
    '/ui/signup',
])
def test_ui_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
