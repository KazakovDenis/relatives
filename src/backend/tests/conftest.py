import asyncio

import pytest
from alembic import command as alembic
from alembic.config import Config

from apps.auth.models import User
from apps.auth.utils import create_session, hash_password
from apps.core.constants import Gender
from apps.core.models import Person, PersonTree, Tree, UserTree
from deps import db as database
from factory import create_app
from httpx import AsyncClient

from . import constants


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def db(event_loop):
    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture(autouse=True, scope='session')
async def apply_migrations(db):
    config = Config()
    config.set_main_option('script_location', 'src.backend:migrations')
    config.set_main_option('sqlalchemy.url', str(db.url))
    alembic.upgrade(config, 'head')
    yield
    alembic.downgrade(config, 'base')


@pytest.fixture
async def app(apply_migrations):
    app = create_app()
    yield app


@pytest.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture
async def user(app):
    obj = await User.objects.create(
        email=constants.ACTIVE_USER_EMAIL,
        password=hash_password(constants.ACTIVE_USER_PASS),
        is_superuser=False,
        is_active=True,
    )
    yield obj
    await obj.delete()


@pytest.fixture
async def inactive_user(app):
    obj = await User.objects.create(
        email=constants.INACTIVE_USER_EMAIL,
        password=hash_password(constants.INACTIVE_USER_PASS),
        is_superuser=False,
        is_active=False,
    )
    yield obj
    await obj.delete()


@pytest.fixture
async def session(user):
    return await create_session(user)


@pytest.fixture
async def tree(user):
    tree = await Tree.objects.create(name='Test')
    await UserTree.objects.create(tree=tree, user=user)
    yield tree
    await tree.delete()


@pytest.fixture
async def person(tree):
    person = await Person.objects.create(name='John', surname='Doe', gender=Gender.MALE)
    await PersonTree.objects.create(tree=tree, person=person)
    yield person
    await person.delete()


@pytest.fixture
async def relative(app):
    person = await Person.objects.create(name='Anna', surname='Doe', gender=Gender.FEMALE)
    yield person
    await person.delete()


@pytest.fixture
def async_teardown(request, event_loop):
    # noinspection PyUnresolvedReferences
    def inner(coro):
        request.addfinalizer(lambda: event_loop.call_soon(coro))
    return inner
