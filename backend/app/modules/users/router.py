from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.security import get_password_hash
from app.models import Role, User
from app.modules.common.schemas import UserSummary
from app.modules.users.schemas import UserCreate, UserResponse, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


def _get_role(db: Session, name: str) -> Role:
    role = db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    return role


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.execute(
        select(User).options(joinedload(User.role)).where(User.id == user_id)
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin"))
) -> list[User]:
    return list(
        db.execute(select(User).options(joinedload(User.role)).order_by(User.id)).scalars().all()
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> User:
    role = _get_role(db, payload.role_name)
    user = User(
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=role,
        is_active=payload.is_active,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    db.refresh(user)
    return _get_user_or_404(db, user.id)


@router.get("/assignable", response_model=list[UserSummary])
def list_assignable_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> list[User]:
    return list(
        db.execute(
            select(User)
            .options(joinedload(User.role))
            .where(User.is_active.is_(True), Role.name.in_(["editor", "employee"]))
            .join(User.role)
            .order_by(User.full_name)
        )
        .scalars()
        .all()
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> User:
    return _get_user_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> User:
    user = _get_user_or_404(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] is not None:
        user.email = data["email"].lower()
    if "password" in data and data["password"]:
        user.password_hash = get_password_hash(data["password"])
    if "full_name" in data and data["full_name"] is not None:
        user.full_name = data["full_name"]
    if "role_name" in data and data["role_name"] is not None:
        user.role = _get_role(db, data["role_name"])
    if "is_active" in data and data["is_active"] is not None:
        user.is_active = data["is_active"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return _get_user_or_404(db, user.id)


@router.delete("/{user_id}", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> User:
    user = _get_user_or_404(db, user_id)
    user.is_active = False
    db.commit()
    return _get_user_or_404(db, user.id)
