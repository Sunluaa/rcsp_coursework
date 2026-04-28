from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import is_admin, is_editor
from app.models import Article, NewsPost, Tag, User
from app.modules.search.schemas import SearchItem, SearchResponse


router = APIRouter(prefix="/search", tags=["search"])


def _snippet(content: str, query: str) -> str:
    text = content.strip().replace("\n", " ")
    if not query:
        return text[:180]
    position = text.lower().find(query.lower())
    if position < 0:
        return text[:180]
    start = max(position - 60, 0)
    end = min(position + len(query) + 120, len(text))
    return text[start:end]


def _apply_visibility(statement, model, current_user: User):
    if is_admin(current_user):
        return statement
    if is_editor(current_user):
        return statement.where(or_(model.status == "published", model.author_id == current_user.id))
    return statement.where(model.status == "published")


def _content_query(model, query: str, category_id: int | None, tag_id: int | None, current_user: User):
    statement = select(model).options(joinedload(model.category), selectinload(model.tags))
    if query:
        term = f"%{query}%"
        statement = statement.where(or_(model.title.ilike(term), model.content.ilike(term)))
    if category_id is not None:
        statement = statement.where(model.category_id == category_id)
    if tag_id is not None:
        statement = statement.join(model.tags).where(Tag.id == tag_id).distinct()
    return _apply_visibility(statement, model, current_user).limit(50)


@router.get("", response_model=SearchResponse)
def search(
    query: str = Query(default="", max_length=120),
    content_type: Literal["articles", "news", "all"] = Query(default="all", alias="type"),
    category_id: int | None = None,
    tag_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    items: list[SearchItem] = []
    cleaned_query = query.strip()

    if content_type in {"articles", "all"}:
        articles = db.execute(
            _content_query(Article, cleaned_query, category_id, tag_id, current_user)
        ).scalars().all()
        items.extend(
            SearchItem(
                type="article",
                id=article.id,
                title=article.title,
                snippet=_snippet(article.content, cleaned_query),
                status=article.status,
                category=article.category,
                tags=article.tags,
            )
            for article in articles
        )

    if content_type in {"news", "all"}:
        news_posts = db.execute(
            _content_query(NewsPost, cleaned_query, category_id, tag_id, current_user)
        ).scalars().all()
        items.extend(
            SearchItem(
                type="news",
                id=news_post.id,
                title=news_post.title,
                snippet=_snippet(news_post.content, cleaned_query),
                status=news_post.status,
                category=news_post.category,
                tags=news_post.tags,
            )
            for news_post in news_posts
        )

    return SearchResponse(items=items[:50])
