from abc import ABC, abstractmethod


class StorageService(ABC):
    provider_name: str

    @abstractmethod
    async def save(self, object_key: str, content: bytes, content_type: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def read(self, object_key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, object_key: str) -> None:
        raise NotImplementedError
