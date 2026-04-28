from pydantic import BaseModel, Field

from app.core.validators import EmailAddress
from app.modules.common.schemas import UserRead


class LoginRequest(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(UserRead):
    pass
