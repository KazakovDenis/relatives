import sentry_sdk
from pydantic import BaseSettings, DirectoryPath


class Settings(BaseSettings):
    PUBLIC_NAME: str = 'Relatives'
    DOMAIN: str = 'localhost'
    DB_DSN: str = ''
    DB_HOST: str = 'localhost'
    DB_NAME: str = 'relatives'
    DB_USER: str = 'postgres'
    DB_PASS: str = 'postgres'
    SENTRY_DSN: str = ''
    MAIL_SERVER: str = 'localhost'
    MAIL_PORT: int = 465
    MAIL_USERNAME: str = 'user@gmail.com'
    MAIL_PASSWORD: str = 'password'
    MAIL_FROM: str = MAIL_USERNAME
    MAIL_SUPPRESS: int = 0
    STATIC_DIR: DirectoryPath = 'static'
    TEMPLATES_DIR: DirectoryPath = 'templates'
    UPLOADS_DIR: DirectoryPath = 'uploads'
    MAX_FILE_SIZE: int = 5_242_880

    class Config:
        env_file = '.env'

    def get_db_dsn(self) -> str:
        if self.DB_DSN:
            return self.DB_DSN
        return 'postgresql+asyncpg://%s:%s@%s:5432/%s' % (self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB_NAME)


settings = Settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
