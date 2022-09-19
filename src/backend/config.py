from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    DB_ADDR: Optional[str] = Field('localhost:5432', env='DB_ADDR')
    DB_USER: Optional[str] = Field('postgres', env='DB_USER')
    DB_PASS: Optional[str] = Field('postgres', env='DB_PASS')
    DB_DSN: Optional[str] = Field(None, env='DB_DSN')

    def get_db_dsn(self) -> str:
        if self.DB_DSN:
            return self.DB_DSN
        return f'postgres+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_ADDR}/relatives'


settings = Settings()
