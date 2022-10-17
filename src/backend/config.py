import sentry_sdk
from pydantic import BaseSettings


class Settings(BaseSettings):
    PUBLIC_NAME: str = 'Relatives'
    DOMAIN: str = 'localhost'
    DB_DSN: str = 'sqlite:///relatives.db'
    SENTRY_DSN: str = ''
    MAIL_SERVER: str = 'localhost'
    MAIL_PORT: int = 465
    MAIL_USERNAME: str = 'user@google.com'
    MAIL_PASSWORD: str = 'password'
    MAIL_SUPPRESS: int = 0

    class Config:
        env_file = '.env'


settings = Settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
