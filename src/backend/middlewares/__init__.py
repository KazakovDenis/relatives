from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from .auth import AuthBackend


middlewares = [
    Middleware(AuthenticationMiddleware, backend=AuthBackend()),
]
