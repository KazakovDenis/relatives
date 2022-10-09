import asyncio
import os

import pytest
from apps.auth.models import User
from apps.auth.utils import create_session, hash_password
from factory import create_app
from fastapi.testclient import TestClient

from . import settings


@pytest.fixture(scope='session')
def app():
    # to discover static files correctly
    os.chdir('src/backend')
    return create_app()


@pytest.fixture(scope='session')
def client(app):
    return TestClient(app)


@pytest.fixture(scope='session')
def user():
    obj = asyncio.run(
        User.objects.create(
            email=settings.ACTIVE_USER_EMAIL,
            password=hash_password(settings.ACTIVE_USER_PASS),
            is_superuser=False,
            is_active=True,
        ),
    )
    yield obj
    asyncio.run(obj.delete())


@pytest.fixture(scope='session')
def blocked_user():
    obj = asyncio.run(
        User.objects.create(
            email=settings.BLOCKED_USER_EMAIL,
            password=hash_password(settings.BLOCKED_USER_PASS),
            is_superuser=False,
            is_active=False,
        ),
    )
    yield obj
    asyncio.run(obj.delete())


@pytest.fixture
async def session(user):
    return await create_session(user)
