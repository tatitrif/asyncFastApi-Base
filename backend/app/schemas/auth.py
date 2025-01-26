from pydantic import BaseModel

from schemas.base import IdResponse
from schemas.user import ValidEmail


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenUserData(IdResponse, ValidEmail):
    username: str
    is_superuser: bool = False
    is_deleted: bool = False
