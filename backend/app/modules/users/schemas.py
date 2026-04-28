from pydantic import BaseModel, Field

from app.core.validators import EmailAddress
from app.modules.common.schemas import RoleName, UserRead


class UserCreate(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role_name: RoleName
    is_active: bool = True


class UserUpdate(BaseModel):
    email: EmailAddress | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role_name: RoleName | None = None
    is_active: bool | None = None


class UserResponse(UserRead):
    pass
