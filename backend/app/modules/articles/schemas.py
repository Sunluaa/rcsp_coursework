from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.common.schemas import (
    AttachmentRead,
    CategoryRead,
    ContentStatus,
    TagRead,
    UserSummary,
)


class ArticleCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=180)
    content: str = Field(min_length=1)
    status: ContentStatus = "draft"
    category_id: int | None = None
    tag_ids: list[int] = []


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=180)
    content: str | None = Field(default=None, min_length=1)
    status: ContentStatus | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    content: str
    status: ContentStatus
    author_id: int
    category_id: int | None = None
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    author: UserSummary
    category: CategoryRead | None = None
    tags: list[TagRead] = []
    attachments: list[AttachmentRead] = []
