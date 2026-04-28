from datetime import UTC, datetime
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.utils import slugify
from app.models import Article, Category, NewsPost, Tag


ContentModel = TypeVar("ContentModel", Article, NewsPost)


def get_category(db: Session, category_id: int | None) -> Category | None:
    if category_id is None:
        return None
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    return category


def get_tags(db: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    unique_ids = list(dict.fromkeys(tag_ids))
    tags = list(db.execute(select(Tag).where(Tag.id.in_(unique_ids))).scalars().all())
    if len(tags) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more tags not found")
    return tags


def resolve_unique_slug(
    db: Session,
    model: type[ContentModel],
    *,
    title: str,
    requested_slug: str | None,
    current_id: int | None = None,
) -> str:
    slug = slugify(requested_slug or title, model.__tablename__.rstrip("s"))
    statement = select(model).where(model.slug == slug)
    if current_id is not None:
        statement = statement.where(model.id != current_id)
    if db.execute(statement).scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    return slug


def apply_content_status(item: Article | NewsPost, status_value: str | None) -> None:
    if status_value is None:
        return
    item.status = status_value
    if status_value == "published" and item.published_at is None:
        item.published_at = datetime.now(UTC)
