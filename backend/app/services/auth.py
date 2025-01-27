from cache.base import AbstractCache
from cache.cache import get_cache
from core import exceptions
from core.config import settings
from repositories.user import UserRepository
from schemas.auth import TokenUserData
from schemas.user import UserCreateSchema, UserCreateDBSchema, UserResponse
from services import celery
from services.base import QueryService

from services.helpers.security import (
    verify_pwd,
    get_token_user,
    create_jwt_tokens,
    get_token_email,
    confirm_pwd,
)


class AuthService(QueryService):
    cache: AbstractCache = get_cache()
    exp: int = settings.CACHE_EXPIRE_SEC

    async def create_one(self, info_form: UserCreateSchema):
        if await UserRepository(self.session).find_one_or_none(
            username=info_form.username
        ):
            raise exceptions.USER_EXCEPTION_CONFLICT_USERNAME_SIGNUP

        if info_form.email:
            if await UserRepository(self.session).find_one_or_none(
                email=info_form.email
            ):
                raise exceptions.USER_EXCEPTION_CONFLICT_EMAIL_SIGNUP

        password = confirm_pwd(info_form.password, info_form.confirmation_password)

        user = info_form.model_dump()
        user["hashed_password"] = password

        _obj = await UserRepository(self.session).add_one(
            UserCreateDBSchema(**user).__dict__
        )
        if _obj:
            await self.session.commit()
            await self.cache.delete_namespace("users")
            return UserResponse.model_validate(_obj)

    async def login(self, form_data):
        if form_data.grant_type == "refresh_token":
            user = await self.authenticate_user_token(token=form_data.refresh_token)
            tokens = create_jwt_tokens(
                user_data=TokenUserData.model_validate(user),
                refresh_token=form_data.refresh_token,
            )
        else:
            user = await self.authenticate_user_pwd(
                username=form_data.username,
                password=form_data.password,
            )
            tokens = create_jwt_tokens(TokenUserData.model_validate(user.to_dict()))
        if not user:
            raise exceptions.CREDENTIALS_EXCEPTION_USER_DB
        _obj = await UserRepository(self.session).edit_one(
            user.id, {"refresh_token": tokens.refresh_token}
        )
        if not _obj:
            raise exceptions.CREDENTIALS_EXCEPTION_LOGIN
        await self.session.commit()
        return tokens

    async def logout(self, token):
        user_token = get_token_user(token)

        user_db = await UserRepository(self.session).find_one_or_none(
            username=user_token.username
        )

        if not user_db or not user_db.refresh_token:
            raise exceptions.CREDENTIALS_EXCEPTION_USER_DB
        _obj = await UserRepository(self.session).edit_one(
            user_db.id, {"refresh_token": None}
        )
        if not _obj:
            raise exceptions.CREDENTIALS_EXCEPTION_LOGOUT
        await self.session.commit()
        return {"detail": "Logout successful"}

    async def forgot_password(self, email):
        data = email.model_dump()
        data_email = data["email"]
        await self._identification_by_email(data_email)
        celery.send_reset_pwd_task.delay(data_email)

        return {
            "detail": f"Письмо отправлено на {data_email} от имени {settings.EMAIL_FROM}, "
            f"проверьте письмо на указанном вами адресе (также в папке Спам)",
            "success": True,
        }

    async def reset_password(self, token, pwd_data):
        email = get_token_email(token)
        user_db = await self._identification_by_email(email)
        password = confirm_pwd(pwd_data.password, pwd_data.confirmation_password)
        await UserRepository(self.session).edit_one(
            user_db.id, dict(hashed_password=password)
        )
        return await self.session.commit()

    async def _identification_by_username(self, username):
        if user := await UserRepository(self.session).find_one_or_none(
            username=username
        ):
            return user
        raise exceptions.USER_EXCEPTION_NOT_FOUND_USER

    async def _identification_by_email(self, email):
        if user := await UserRepository(self.session).find_one_or_none(email=email):
            return user
        raise exceptions.USER_EXCEPTION_NOT_FOUND_USER_EMAIL

    async def authenticate_user_pwd(self, username, password):
        user = await self._identification_by_username(username=username)
        if not user or not verify_pwd(password, user.hashed_password):
            raise exceptions.USER_EXCEPTION_WRONG_PARAMETER
        return user

    async def authenticate_user_token(self, token):
        user = get_token_user(token, "refresh")
        user_db = await UserRepository(self.session).find_one_or_none(
            username=user.username
        )
        if not user_db:
            raise exceptions.USER_EXCEPTION_WRONG_PARAMETER
        return user
