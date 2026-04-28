from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Role, User
from app.modules.common.schemas import RoleRead


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleRead])
def list_roles(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Role]:
    return list(db.execute(select(Role).order_by(Role.id)).scalars().all())
