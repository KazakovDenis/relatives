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


async def email_reset_password(email: EmailStr, token: str):
    await send_email(
        subject='Password reset requested',
        recipients=[email],
        template='reset_password.html',
        ctx={
            'domain': settings.DOMAIN,
            'token': token,
        },
    )
