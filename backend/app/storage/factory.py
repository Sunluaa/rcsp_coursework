from functools import lru_cache

from app.core.config import get_settings
from app.storage.base import StorageService
from app.storage.local import LocalStorageService
from app.storage.s3 import S3StorageService


@lru_cache
def get_storage_service() -> StorageService:
    settings = get_settings()
    if settings.storage_provider == "s3":
        return S3StorageService(settings)
    return LocalStorageService(settings.local_storage_path)
