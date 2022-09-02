from apps.auth.models import Session, User
from apps.auth.utils import token_to_uuid
from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      AuthenticationError, BaseUser)


class RequestUser(BaseUser):

    def __init__(self, user: User):
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        return self.user.is_active

    @property
    def display_name(self) -> str:
        return self.user.name


class AuthBackend(AuthenticationBackend):
    cookie = 'Authorization'

    async def authenticate(self, conn):
        if (
            'login' in conn.scope['path']
            or 'static' in conn.scope['path']
            or conn.scope['path'] == '/'
        ):
            # do auth in a handler
            return

        if self.cookie not in conn.cookies:
            raise AuthenticationError('Not authenticated')

        scheme, token = conn.cookies[self.cookie].split()
        if scheme.lower() != 'bearer':
            return

        if not (as_uuid := token_to_uuid(token)):
            return

        session = await Session.objects.select_related('user').first(token=as_uuid)
        if not session:
            return
        return AuthCredentials(['authenticated']), RequestUser(session.user)
