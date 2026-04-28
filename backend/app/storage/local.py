from pathlib import Path

from app.storage.base import StorageService


class LocalStorageService(StorageService):
    provider_name = "local"

    def __init__(self, base_path: str) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve(self, object_key: str) -> Path:
        path = (self.base_path / object_key).resolve()
        base = self.base_path.resolve()
        if base not in path.parents and path != base:
            raise ValueError("Invalid object key")
        return path

    async def save(self, object_key: str, content: bytes, content_type: str) -> str:
        path = self._resolve(object_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return object_key

    async def read(self, object_key: str) -> bytes:
        return self._resolve(object_key).read_bytes()

    async def delete(self, object_key: str) -> None:
        path = self._resolve(object_key)
        if path.exists():
            path.unlink()
