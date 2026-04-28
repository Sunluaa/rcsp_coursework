from pydantic import BaseModel, Field

from app.modules.common.schemas import CategoryRead


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str | None = Field(default=None, max_length=160)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    slug: str | None = Field(default=None, max_length=160)
    description: str | None = None


class CategoryResponse(CategoryRead):
    pass
