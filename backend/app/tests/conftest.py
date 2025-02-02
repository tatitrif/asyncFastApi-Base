from typing import Any
from collections.abc import Callable, Awaitable

import pytest
from faker import Faker
from httpx import AsyncClient, ASGITransport

from core.session_manager import db_manager
from main import app
from schemas.user import UserCreateSchema, UserResponse
from services.user import UserService
from tests import test_settings

BASE_URL = f"http://127.0.0.1:8000{test_settings.API_V1_STR}"


@pytest.fixture(scope="session")
def fake():
    return Faker()


@pytest.fixture(scope="session")
async def engine():
    """Create a fresh database for each test."""
    db_manager.init(
        test_settings.SQLALCHEMY_DATABASE_URI, {"echo": False, "future": True}
    )
    await db_manager.create_all()
    yield engine
    await db_manager.drop_all()


@pytest.fixture(scope="function")
async def client(engine) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="function")
def registered_user(
    fake: Faker,
) -> Callable[[AsyncClient, UserCreateSchema], Awaitable[Any]]:
    """Factory fixture to registered user."""

    async def _registered(
        client: AsyncClient,
        username: str = None,
        email: str = None,
        password: str = None,
        is_superuser: bool = None,
    ) -> tuple[UserResponse, str]:
        password_in = password or fake.password()
        username_in = username or fake.user_name()
        email_in = email or fake.email()
        user_in = UserCreateSchema(
            username=username_in,
            email=email_in,
            password=password_in,
            confirmation_password=password_in,
        )
        payload = user_in.model_dump()
        # регистрация
        response_reg = await client.post("/auth/signup", json=payload)

        data_out = response_reg.json()
        if is_superuser:
            user_in_id = response_reg.json()["id"]
            async with db_manager.session() as session:
                await UserService(session).edit_superuser(user_in_id, is_superuser)

        return data_out, password_in

    return _registered


@pytest.fixture(scope="function")
def authenticate_client(
    registered_user: Callable, fake: Faker
) -> Callable[[AsyncClient, UserResponse], Awaitable[AsyncClient]]:
    """Factory fixture to authenticate."""

    async def _authenticate_client(
        client: AsyncClient,
        data: tuple[UserResponse, str] = None,
        is_superuser: bool = None,
    ) -> AsyncClient:
        if not data:
            data = await registered_user(client, is_superuser=is_superuser)

        user, password = data
        username = user.get("username")
        payload = dict(grant_type="password", username=username, password=password)
        response_auth = await client.post("/auth/token", data=payload)
        body = response_auth.json()
        client.headers["Authorization"] = f"Bearer {body["refresh_token"]}"
        return client

    return _authenticate_client


@pytest.fixture
def test_user_in_db(
    client: AsyncClient, registered_user: Callable, fake: Faker
) -> Callable:
    """Create a test user in the database."""

    async def _test_user_in_db() -> UserResponse:
        data = await registered_user(client)
        user, password = data
        return user

    return _test_user_in_db


@pytest.fixture
def batch_test_user_in_db(
    client: AsyncClient, registered_user: Callable, fake: Faker
) -> Callable:
    """Create a test user in the database."""

    async def _batch_test_user_in_db(count: int | None = 10) -> UserResponse:
        for _ in range(count):
            await registered_user(client)

    return _batch_test_user_in_db
