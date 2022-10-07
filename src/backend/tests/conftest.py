import os

import pytest
from factory import create_app
from fastapi.testclient import TestClient


@pytest.fixture(scope='session')
def app():
    # to discover static files correctly
    os.chdir('src/backend')
    return create_app()


@pytest.fixture(scope='session')
def client(app):
    return TestClient(app)
