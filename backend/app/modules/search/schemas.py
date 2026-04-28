from pydantic import BaseModel

from app.modules.common.schemas import CategoryRead, TagRead


class SearchItem(BaseModel):
    type: str
    id: int
    title: str
    snippet: str
    status: str
    category: CategoryRead | None = None
    tags: list[TagRead] = []


class SearchResponse(BaseModel):
    items: list[SearchItem]
