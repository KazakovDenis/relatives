from typing import Optional

import sentry_sdk
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    DB_DSN: str = Field('sqlite:///relatives.db', env='DB_DSN')
    SENTRY_DSN: Optional[str] = Field(None, env='SENTRY_DSN')


settings = Settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
