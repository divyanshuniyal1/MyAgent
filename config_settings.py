# config_settings.py

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MICROSOFT_TENANT_ID: str
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/sso/azure/callback"
    JWT_SECRET: str = "supersecretkey"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()