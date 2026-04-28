from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.validators import EmailAddress


RoleName = Literal["admin", "editor", "employee"]
ContentStatus = Literal["draft", "published", "archived"]
TaskStatus = Literal["todo", "in_progress", "done", "cancelled"]
TaskPriority = Literal["low", "medium", "high"]


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: RoleName
    description: str | None = None


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailAddress
    full_name: str
    role: RoleRead
    is_active: bool


class UserRead(UserSummary):
    created_at: datetime
    updated_at: datetime


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    content_type: str
    size: int = Field(ge=0)
    storage_provider: str
    article_id: int | None = None
    news_post_id: int | None = None
    uploaded_by: int
    created_at: datetime
