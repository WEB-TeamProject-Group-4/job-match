from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = 'job-match'
    DB_URL: str = Field(default='dummy', json_schema_extra={'env': 'DB_URL'})
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, json_schema_extra={'env': 'ACCESS_TOKEN_EXPIRE_MINUTES'})
    EMAIL_TOKEN_EXPIRE_MINUTES: int = Field(default=30, json_schema_extra={'env': 'EMAIL_TOKEN_EXPIRE_MINUTES'})
    ALGORITHM: str = Field(default='HS256', json_schema_extra={'env': 'ALGORITHM'})
    MAIL_USERNAME: str = Field(default='dummy@mail.com', json_schema_extra={'env': 'MAIL_USERNAME'})
    MAIL_PASSWORD: str = Field(default='dummy', json_schema_extra={'env': 'MAIL_PASSWORD'})
    MAIL_SERVER: str = Field(default='dummy', json_schema_extra={'env': 'MAIL_SERVER'})
    VALIDATE_CERTS: bool = Field(default=False, json_schema_extra={'env': 'VALIDATE_CERTS'})

    model_config = SettingsConfigDict(env_file='dotenv.env', extra='allow')


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
