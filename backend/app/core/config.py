from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "KnowledgeBaZa"
    environment: str = "local"
    database_url: str
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    bcrypt_rounds: int = 12
    cors_origins: str = ""

    storage_provider: Literal["local", "s3"] = "local"
    local_storage_path: str = "uploads"
    max_upload_size_bytes: int = 10 * 1024 * 1024

    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str = "auto"
    s3_public_url: str | None = None

    seed_admin_email: str = "admin@knowledgebaza.local"
    seed_admin_password: str | None = None
    seed_editor_email: str = "editor@knowledgebaza.local"
    seed_editor_password: str | None = None
    seed_employee_email: str = "employee@knowledgebaza.local"
    seed_employee_password: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
