import pytest
from apps.auth.models import User
from apps.auth.utils import create_session, hash_password
from apps.core.constants import Gender
from apps.core.models import Person, PersonTree, Tree, UserTree
from deps import db
from factory import create_app
from fastapi.testclient import TestClient

from . import settings


@pytest.fixture
async def app(event_loop):
    app = create_app()
    await db.connect()
    yield app
    await db.disconnect()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
async def user(app):
    obj = await User.objects.create(
        email=settings.ACTIVE_USER_EMAIL,
        password=hash_password(settings.ACTIVE_USER_PASS),
        is_superuser=False,
        is_active=True,
    )
    yield obj
    await obj.delete()


@pytest.fixture
async def inactive_user(app):
    obj = await User.objects.create(
        email=settings.INACTIVE_USER_EMAIL,
        password=hash_password(settings.INACTIVE_USER_PASS),
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
        request.addfinalizer(lambda: event_loop.run_until_complete(coro))
    return inner
