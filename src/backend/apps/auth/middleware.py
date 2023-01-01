from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser

from apps.auth.models import Session, User
from apps.auth.utils import Scopes, token_to_uuid


class RequestUser(BaseUser):

    def __init__(self, user: User):
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        # noinspection PyTypeChecker
        return self.user.is_active

    @property
    def display_name(self) -> str:
        return self.user.name

    @property
    def identity(self):
        return self.user.id


class AuthBackend(AuthenticationBackend):
    cookie = 'Authorization'
    allowed_paths = (
        '/login',
        '/signup',
        '/activate',
        '/join',
        '/verify-email',
        '/forbidden',
        '/static',
    )

    async def authenticate(self, conn):
        # todo: move to Security
        if self.cookie not in conn.cookies:
            if self.skip_for_path(conn.scope['path']):
                return
            raise AuthenticationError('Not authenticated')

        auth_row = conn.cookies.get(self.cookie, '').split()
        if len(auth_row) < 2:
            return

        scheme, token = auth_row
        if scheme.lower() != 'bearer':
            return

        if not (as_uuid := token_to_uuid(token)):
            return

        session = await Session.objects.select_related('user').get_or_none(token=as_uuid)
        if not session:
            return
        user = session.user
        scope = Scopes.ADMIN if user.is_superuser else Scopes.USER
        return AuthCredentials([scope]), RequestUser(user)

    def skip_for_path(self, path) -> bool:
        if path == '/':
            return True
        for part in self.allowed_paths:
            if path.count(part):
                return True
        return False
