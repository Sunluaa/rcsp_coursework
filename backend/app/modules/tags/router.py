from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.utils import slugify
from app.models import Tag, User
from app.modules.tags.schemas import TagCreate, TagResponse, TagUpdate


router = APIRouter(prefix="/tags", tags=["tags"])


def _get_tag_or_404(db: Session, tag_id: int) -> Tag:
    tag = db.execute(
        select(Tag).options(selectinload(Tag.articles), selectinload(Tag.news_posts)).where(Tag.id == tag_id)
    ).scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.get("", response_model=list[TagResponse])
def list_tags(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Tag]:
    return list(db.execute(select(Tag).order_by(Tag.name)).scalars().all())


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Tag:
    tag = Tag(name=payload.name, slug=slugify(payload.slug or payload.name, "tag"))
    db.add(tag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    db.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Tag:
    tag = _get_tag_or_404(db, tag_id)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        tag.name = data["name"]
    if "slug" in data and data["slug"] is not None:
        tag.slug = slugify(data["slug"], "tag")
    elif "name" in data and data["name"] is not None:
        tag.slug = slugify(data["name"], "tag")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> None:
    tag = _get_tag_or_404(db, tag_id)
    tag.articles.clear()
    tag.news_posts.clear()
    db.delete(tag)
    db.commit()
