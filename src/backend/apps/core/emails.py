from pydantic import EmailStr

from config import settings
from tools.notifications.email import send_email

from ..auth.models import User
from .models import Tree


async def email_joined_tree(email: EmailStr, user: User, tree: Tree):
    await send_email(
        subject=f'{settings.PUBLIC_NAME}: New user has joined your tree',
        recipients=[email],
        template='joined.html',
        ctx={
            'domain': settings.DOMAIN,
            'user': user,
            'tree': tree,
        },
    )
