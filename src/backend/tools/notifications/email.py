from config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr


smtp_client = FastMail(
    ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=EmailStr(settings.MAIL_USERNAME),
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.PUBLIC_NAME,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER='templates/email',
        SUPPRESS_SEND=settings.MAIL_SUPPRESS,
    )
)


async def send_email(subject: str, recipients: list[EmailStr], ctx: dict):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=ctx,
        subtype=MessageType.html,
    )
    await smtp_client.send_message(message, template_name='signup.html')


async def verify_email(email: EmailStr, token: str):
    await send_email(
        subject=f'Welcome to {settings.PUBLIC_NAME}',
        recipients=[email],
        ctx={
            'domain': settings.DOMAIN,
            'token': token,
        },
    )
