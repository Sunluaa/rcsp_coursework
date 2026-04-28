from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.utils import slugify
from app.models import Article, Category, NewsPost, User
from app.modules.categories.schemas import CategoryCreate, CategoryResponse, CategoryUpdate


router = APIRouter(prefix="/categories", tags=["categories"])


def _get_category_or_404(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Category]:
    return list(db.execute(select(Category).order_by(Category.name)).scalars().all())


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Category:
    category = Category(
        name=payload.name,
        slug=slugify(payload.slug or payload.name, "category"),
        description=payload.description,
    )
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Category:
    category = _get_category_or_404(db, category_id)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        category.name = data["name"]
    if "slug" in data and data["slug"] is not None:
        category.slug = slugify(data["slug"], "category")
    elif "name" in data and data["name"] is not None:
        category.slug = slugify(data["name"], "category")
    if "description" in data:
        category.description = data["description"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> None:
    category = _get_category_or_404(db, category_id)
    is_used = db.execute(
        select(Article.id).where(Article.category_id == category_id).limit(1)
    ).first() or db.execute(select(NewsPost.id).where(NewsPost.category_id == category_id).limit(1)).first()
    if is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category is in use")
    db.delete(category)
    db.commit()
