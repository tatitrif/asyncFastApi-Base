from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Form
from fastapi import Request, WebSocket
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core import exceptions
from core.config import settings
from schemas.auth import TokenUserData, TokenResponse


def now_utc():
    return datetime.now(timezone.utc)


# ref : https://github.com/tiangolo/fastapi/issues/2031
class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    """Модифицированная аутентификация"""

    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)


oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


class OAuth2PasswordAndRefreshRequestForm(OAuth2PasswordRequestForm):
    """Модификация формы OAuth2PasswordBearer"""

    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password|refresh_token"),
        username: str = Form(default=""),
        password: str = Form(default=""),
        refresh_token: str = Form(default=""),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=""),
        client_secret: str | None = Form(default=""),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.scopes = scope.split()
        self.refresh_token = refresh_token


def to_bits(*args):
    return tuple(s.encode("utf-8") for s in args)


def to_str(*args):
    return tuple(b.decode("utf-8") for b in args)


def hash_pwd(pwd: str) -> str:
    salt = bcrypt.gensalt()
    return to_str(bcrypt.hashpw(*to_bits(pwd), salt))[0]


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(*to_bits(plain_pwd, hashed_pwd))


def encode_token(data: dict) -> str:
    return jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)


def decode_token(data) -> dict:
    return jwt.decode(data, settings.SECRET_KEY, [settings.ALGORITHM])


def create_token(data: dict, delta: timedelta) -> str:
    """Создает JWT токен.
    Args:
        data: Полезная нагрузка.
        delta: Время жизни токена.

    Returns:
        Закодированный токен.
    """
    expires_delta = now_utc() + delta
    data.update({"exp": expires_delta})

    return encode_token(data)


def create_jwt_tokens(
    user_data: TokenUserData, refresh_token: str | None = None
) -> TokenResponse:
    """Создает пару токенов: access_token, refresh_token.
    Если есть refresh токен, то он не обновляется
    Args:
        user_data: данные пользователя,
        refresh_token: refresh токен.

    Returns:
        `TokenResponse`.
    """
    access_token = create_token(
        {**user_data.model_dump(), "token_type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    if not refresh_token:
        refresh_token: str = create_token(
            {**user_data.model_dump(), "token_type": "refresh"},
            timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS),
        )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def verify_token(token: str, token_type: str | None) -> TokenUserData:
    """Проверяет токен на валидность.
    Если есть нет типа токена, то тип не проверяется.
    Args:
        token: Закодированный токен,
        token_type: Тип токена (access или refresh).

    Returns:
        TokenUserData: Схема данных о пользователе.

    Raises:
        CredentialsException: Если токен недействителен.
    """
    try:
        payload = decode_token(token)
        if token_type:
            payload_token_type: str = payload.get("token_type")
            if not payload_token_type or payload_token_type != token_type:
                raise exceptions.CREDENTIALS_EXCEPTION_TYPE
        user = TokenUserData(**payload)
        if user is None:
            raise exceptions.CREDENTIALS_EXCEPTION_USER
        token_expiration: int = payload.get("exp", 0)
        if token_expiration < now_utc().timestamp():
            raise exceptions.CREDENTIALS_EXCEPTION_EXPIRED

        return user
    except jwt.PyJWTError:
        raise exceptions.CREDENTIALS_EXCEPTION_INVALID


def get_token_user(token, token_type: str | None = None) -> TokenUserData:
    """Возвращает данные пользователя из токена.

    Args:
        token: Закодированный токен.
        token_type: Тип токена (access или refresh).

    Returns:
        TokenUserData: Схема данных о пользователе.

    Raises:
        CredentialsException: Если токен недействителен.
    """
    if verify_token(token, token_type):
        payload = decode_token(token)
        user = TokenUserData(**payload)
        return user
