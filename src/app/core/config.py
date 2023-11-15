from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = 'job-match'
    DB_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    EMAIL_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    VALIDATE_CERTS: bool

    model_config = SettingsConfigDict(env_file='dotenv.env', extra='allow')


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
