from pydantic import EmailStr

from config import settings
from tools.notifications.email import send_email


async def email_verify(email: EmailStr, token: str):
    await send_email(
        subject=f'Welcome to {settings.PUBLIC_NAME}',
        recipients=[email],
        template='signup.html',
        ctx={
            'domain': settings.DOMAIN,
            'token': token,
        },
    )
