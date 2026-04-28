from pydantic import BaseModel, Field

from app.modules.common.schemas import TagRead


class TagCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    slug: str | None = Field(default=None, max_length=120)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    slug: str | None = Field(default=None, max_length=120)


class TagResponse(TagRead):
    pass
