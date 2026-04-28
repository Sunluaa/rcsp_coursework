from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.permissions import ensure_can_manage_content, ensure_can_view_content, is_admin, is_editor
from app.models import NewsPost, User
from app.modules.content_utils import apply_content_status, get_category, get_tags, resolve_unique_slug
from app.modules.news.schemas import NewsPostCreate, NewsPostResponse, NewsPostUpdate


router = APIRouter(prefix="/news", tags=["news"])


def _news_options():
    return (
        joinedload(NewsPost.author).joinedload(User.role),
        joinedload(NewsPost.category),
        selectinload(NewsPost.tags),
        selectinload(NewsPost.attachments),
    )


def _visible_news_query(current_user: User):
    statement = select(NewsPost).options(*_news_options()).order_by(desc(NewsPost.updated_at))
    if is_admin(current_user):
        return statement
    if is_editor(current_user):
        return statement.where(or_(NewsPost.status == "published", NewsPost.author_id == current_user.id))
    return statement.where(NewsPost.status == "published")


def _get_news_or_404(db: Session, news_post_id: int) -> NewsPost:
    news_post = db.execute(
        select(NewsPost).options(*_news_options()).where(NewsPost.id == news_post_id)
    ).scalar_one_or_none()
    if news_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News post not found")
    return news_post


@router.get("", response_model=list[NewsPostResponse])
def list_news(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[NewsPost]:
    return list(db.execute(_visible_news_query(current_user)).scalars().all())


@router.post("", response_model=NewsPostResponse, status_code=status.HTTP_201_CREATED)
def create_news_post(
    payload: NewsPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> NewsPost:
    category = get_category(db, payload.category_id)
    tags = get_tags(db, payload.tag_ids)
    news_post = NewsPost(
        title=payload.title,
        slug=resolve_unique_slug(db, NewsPost, title=payload.title, requested_slug=payload.slug),
        content=payload.content,
        status=payload.status,
        author_id=current_user.id,
        category=category,
    )
    apply_content_status(news_post, payload.status)
    news_post.tags = tags
    db.add(news_post)
    db.commit()
    return _get_news_or_404(db, news_post.id)


@router.get("/{news_post_id}", response_model=NewsPostResponse)
def get_news_post(
    news_post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NewsPost:
    news_post = _get_news_or_404(db, news_post_id)
    ensure_can_view_content(current_user, news_post)
    return news_post


@router.patch("/{news_post_id}", response_model=NewsPostResponse)
def update_news_post(
    news_post_id: int,
    payload: NewsPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> NewsPost:
    news_post = _get_news_or_404(db, news_post_id)
    ensure_can_manage_content(current_user, news_post)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        news_post.title = data["title"]
    if "slug" in data and data["slug"] is not None:
        news_post.slug = resolve_unique_slug(
            db, NewsPost, title=news_post.title, requested_slug=data["slug"], current_id=news_post.id
        )
    if "content" in data and data["content"] is not None:
        news_post.content = data["content"]
    if "category_id" in data:
        news_post.category = get_category(db, data["category_id"])
    if "tag_ids" in data and data["tag_ids"] is not None:
        news_post.tags = get_tags(db, data["tag_ids"])
    if "status" in data:
        apply_content_status(news_post, data["status"])
    db.commit()
    return _get_news_or_404(db, news_post.id)


@router.delete("/{news_post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_post(
    news_post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> None:
    news_post = _get_news_or_404(db, news_post_id)
    ensure_can_manage_content(current_user, news_post)
    db.delete(news_post)
    db.commit()


@router.post("/{news_post_id}/publish", response_model=NewsPostResponse)
def publish_news_post(
    news_post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> NewsPost:
    news_post = _get_news_or_404(db, news_post_id)
    ensure_can_manage_content(current_user, news_post)
    apply_content_status(news_post, "published")
    db.commit()
    return _get_news_or_404(db, news_post.id)


@router.post("/{news_post_id}/archive", response_model=NewsPostResponse)
def archive_news_post(
    news_post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> NewsPost:
    news_post = _get_news_or_404(db, news_post_id)
    ensure_can_manage_content(current_user, news_post)
    apply_content_status(news_post, "archived")
    db.commit()
    return _get_news_or_404(db, news_post.id)
