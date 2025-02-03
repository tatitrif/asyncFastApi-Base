from cache.base import AbstractCache
from cache.cache import get_cache
from core import exceptions
from core.config import settings
from repositories.user import UserRepository
from schemas.auth import TokenUserData
from schemas.base import IdResponse
from schemas.page import PageResponse, PageInfoResponse, PagedParamsSchema
from schemas.user import UserUpdateSchema, UserResponse, UserFilterSchema
from services.base import QueryService
from services.helpers.page import paginate


class UserService(QueryService):
    cache: AbstractCache = get_cache()
    exp: int = settings.CACHE_EXPIRE_SEC

    async def edit_me(
        self,
        current_active_user: TokenUserData,
        update_form: UserUpdateSchema,
    ):
        data = update_form.model_dump(exclude_none=True)
        if update_form.email:
            if await UserRepository(self.session).find_one_or_none(
                email=update_form.email
            ):
                raise exceptions.USER_EXCEPTION_CONFLICT_EMAIL_SIGNUP
        _obj = await UserRepository(self.session).edit_one(current_active_user.id, data)
        if _obj:
            cache_key = f"user:{current_active_user.id}"
            await self.cache.delete(cache_key)

            await self.session.commit()
            await self.session.refresh(_obj)
            return UserResponse.model_validate(_obj)

    async def find_one(
        self,
        user_id: IdResponse,
    ):
        cache_key = f"user:{user_id}"
        if cache_user := await self.cache.get(cache_key):
            return cache_user

        _obj = await UserRepository(self.session).find_one_or_none(id=user_id)
        if _obj:
            await self.cache.set(cache_key, _obj, self.exp)

            return UserResponse.model_validate(_obj)
        raise exceptions.USER_EXCEPTION_NOT_FOUND_USER

    async def edit_one(
        self,
        user_id: IdResponse,
        update_form: UserUpdateSchema,
    ):
        data = update_form.model_dump()
        if update_form.email:
            if await UserRepository(self.session).find_one_or_none(email=data["email"]):
                raise exceptions.USER_EXCEPTION_CONFLICT_EMAIL_SIGNUP

        if not await UserRepository(self.session).find_one_or_none(id=user_id):
            raise exceptions.USER_EXCEPTION_NOT_FOUND_USER

        _obj = await UserRepository(self.session).edit_one(user_id, data)
        if _obj:
            cache_key = f"user:{user_id}"
            await self.cache.delete(cache_key)

            await self.session.commit()
            await self.session.refresh(_obj)
            return UserResponse.model_validate(_obj)

    async def delete_one(self, user_id: IdResponse):
        if await UserRepository(self.session).find_one_or_none(id=user_id):
            _obj = await UserRepository(self.session).edit_one(
                _id=user_id, data=dict(is_deleted=1)
            )
            if _obj:
                cache_key = f"user:{user_id}"
                await self.cache.delete(cache_key)

                await self.session.commit()
                await self.session.refresh(_obj)
                return {"detail": f"Deleted id={_obj.id}"}

        raise exceptions.USER_EXCEPTION_NOT_FOUND_USER

    async def find_all(
        self,
        limit_offset: PagedParamsSchema,
        filter_schema: UserFilterSchema,
    ):
        filters = filter_schema.model_dump(exclude_none=True)
        limit_offset = limit_offset.model_dump(exclude_none=True)

        cache_key_filters = ":".join(f"{k}:{v}" for k, v in filters.items())
        cache_key_limit_offset = ":".join(f"{k}:{v}" for k, v in limit_offset.items())
        cache_key = f"users:{cache_key_filters}:{cache_key_limit_offset}"

        if cache_users := await self.cache.get(cache_key):
            return cache_users
        page_entities = await UserRepository(self.session).find_by_page(
            **limit_offset, **filters
        )
        total = await UserRepository(self.session).count(**filters)
        pagination_info = paginate(**limit_offset, total=total)
        if not page_entities:
            raise exceptions.USER_EXCEPTION_NOT_FOUND_PAGE

        db_users = PageResponse(
            page_info=PageInfoResponse(**pagination_info),
            page_data=[UserResponse.model_validate(entity) for entity in page_entities],
        )

        await self.cache.set(cache_key, db_users, self.exp)

        return db_users

    async def edit_superuser(
        self,
        user_id: IdResponse,
        is_superuser: bool,
    ):
        if not await UserRepository(self.session).find_one_or_none(id=user_id):
            raise exceptions.USER_EXCEPTION_NOT_FOUND_USER

        _obj = await UserRepository(self.session).edit_one(
            user_id, dict(is_superuser=is_superuser)
        )
        if _obj:
            cache_key = f"user:{user_id}"
            await self.cache.delete(cache_key)

            await self.session.commit()
            await self.session.refresh(_obj)
            return UserResponse.model_validate(_obj)
