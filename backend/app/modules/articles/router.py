from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.permissions import ensure_can_manage_content, ensure_can_view_content, is_admin, is_editor
from app.models import Article, User
from app.modules.articles.schemas import ArticleCreate, ArticleResponse, ArticleUpdate
from app.modules.content_utils import apply_content_status, get_category, get_tags, resolve_unique_slug


router = APIRouter(prefix="/articles", tags=["articles"])


def _article_options():
    return (
        joinedload(Article.author).joinedload(User.role),
        joinedload(Article.category),
        selectinload(Article.tags),
        selectinload(Article.attachments),
    )


def _visible_article_query(current_user: User):
    statement = select(Article).options(*_article_options()).order_by(desc(Article.updated_at))
    if is_admin(current_user):
        return statement
    if is_editor(current_user):
        return statement.where(or_(Article.status == "published", Article.author_id == current_user.id))
    return statement.where(Article.status == "published")


def _get_article_or_404(db: Session, article_id: int) -> Article:
    article = db.execute(
        select(Article).options(*_article_options()).where(Article.id == article_id)
    ).scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.get("", response_model=list[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Article]:
    return list(db.execute(_visible_article_query(current_user)).scalars().all())


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Article:
    category = get_category(db, payload.category_id)
    tags = get_tags(db, payload.tag_ids)
    article = Article(
        title=payload.title,
        slug=resolve_unique_slug(db, Article, title=payload.title, requested_slug=payload.slug),
        content=payload.content,
        status=payload.status,
        author_id=current_user.id,
        category=category,
    )
    apply_content_status(article, payload.status)
    article.tags = tags
    db.add(article)
    db.commit()
    return _get_article_or_404(db, article.id)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Article:
    article = _get_article_or_404(db, article_id)
    ensure_can_view_content(current_user, article)
    return article


@router.patch("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Article:
    article = _get_article_or_404(db, article_id)
    ensure_can_manage_content(current_user, article)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        article.title = data["title"]
    if "slug" in data and data["slug"] is not None:
        article.slug = resolve_unique_slug(
            db, Article, title=article.title, requested_slug=data["slug"], current_id=article.id
        )
    if "content" in data and data["content"] is not None:
        article.content = data["content"]
    if "category_id" in data:
        article.category = get_category(db, data["category_id"])
    if "tag_ids" in data and data["tag_ids"] is not None:
        article.tags = get_tags(db, data["tag_ids"])
    if "status" in data:
        apply_content_status(article, data["status"])
    db.commit()
    return _get_article_or_404(db, article.id)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> None:
    article = _get_article_or_404(db, article_id)
    ensure_can_manage_content(current_user, article)
    db.delete(article)
    db.commit()


@router.post("/{article_id}/publish", response_model=ArticleResponse)
def publish_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Article:
    article = _get_article_or_404(db, article_id)
    ensure_can_manage_content(current_user, article)
    apply_content_status(article, "published")
    db.commit()
    return _get_article_or_404(db, article.id)


@router.post("/{article_id}/archive", response_model=ArticleResponse)
def archive_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Article:
    article = _get_article_or_404(db, article_id)
    ensure_can_manage_content(current_user, article)
    apply_content_status(article, "archived")
    db.commit()
    return _get_article_or_404(db, article.id)
