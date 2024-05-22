from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")
