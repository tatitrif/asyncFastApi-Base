from datetime import timedelta
from typing import Callable

from faker import Faker
from fastapi import status
from httpx import AsyncClient

from schemas.user import UserCreateSchema
from services.helpers.security import create_token
from tests import test_settings


async def test_signup(client: AsyncClient, fake: Faker) -> None:
    """Test user registration"""

    password = fake.password()
    username = fake.user_name()
    user_in = UserCreateSchema(
        username=username,
        email=fake.email(),
        password=password,
        confirmation_password=password,
    )
    payload = user_in.model_dump()
    # регистрация с правильными данными
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data_out = response.json()
    # Проверим ответ после регистрации
    assert data_out["email"] == user_in.email
    assert data_out["username"] == user_in.username
    assert "password" not in data_out
    assert "confirmation_password" not in data_out
    assert "hashed_password" not in data_out
    assert "id" in data_out
    assert "image" in data_out
    assert "fullname" in data_out
    assert "created_at" in data_out

    # дубликат регистрации с правильными данными
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT

    user_in = dict(
        username=username,
        email=fake.email(),
        password=password,
        confirmation_password="",
    )
    # регистрация с не правильные данные
    response = await client.post("/auth/signup", json=user_in)
    assert response.status_code != status.HTTP_201_CREATED
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_token(
    client: AsyncClient, fake: Faker, registered_user: Callable
) -> None:
    """Test user login"""

    username = fake.user_name()
    password = fake.password()
    await registered_user(client, username=username, password=password)

    # логинимся через пароль с правильными данными
    payload_pwd = dict(grant_type="password", username=username, password=password)
    response = await client.post("/auth/token", data=payload_pwd)
    assert response.status_code == status.HTTP_200_OK
    body_pwd = response.json()
    assert body_pwd["access_token"]
    assert body_pwd["refresh_token"]

    # логинимся через refresh_token с правильными данными
    payload_refresh = dict(
        grant_type="refresh_token", refresh_token=body_pwd["refresh_token"]
    )
    response = await client.post("/auth/token", data=payload_refresh)
    assert response.status_code == status.HTTP_200_OK
    body_refresh = response.json()
    assert body_refresh["access_token"]
    assert body_refresh["refresh_token"]

    # логинимся через пароль с ошибочными данными
    payload = dict(username=username, password=username)
    response = await client.post("/auth/token", data=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # логинимся через refresh_token с ошибочными данными
    payload_refresh = dict(
        grant_type="refresh_token", refresh_token=body_pwd["access_token"]
    )
    response = await client.post("/auth/token", data=payload_refresh)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout(client: AsyncClient, authenticate_client: Callable) -> None:
    """Test user logout"""

    response = await client.post("/auth/logout")

    # не авторизован
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await authenticate_client(client)
    response = await client.post("/auth/logout")

    # авторизован
    assert response.status_code == status.HTTP_200_OK

    response = await client.post("/auth/logout")

    # уже не авторизован
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_forgot_password(
    client: AsyncClient,
    registered_user: Callable,
) -> None:
    response = await client.post("/auth/forgot-password", data={})

    # пустой email
    assert response.status_code == status.HTTP_404_NOT_FOUND

    email = "email@test.ru"
    response = await client.post("/auth/forgot-password", data=dict(email=email))

    # не существует email
    assert response.status_code == status.HTTP_404_NOT_FOUND

    await registered_user(client, email=email)
    response = await client.post("/auth/forgot-password", data=dict(email=email))

    # создан email
    assert response.status_code == status.HTTP_200_OK


async def test_reset_password_token(
    client: AsyncClient,
    registered_user: Callable,
) -> None:
    email = "email@test.ru"
    token = create_token(
        data=dict(email=email),
        delta=timedelta(minutes=test_settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES),
    )
    data_pwd = dict(password="string", confirmation_password="string")

    await registered_user(client, email=email)
    response = await client.post(f"/auth/reset-password/{token}", data=dict())

    # пустой data
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = await client.post("/auth/reset-password", json=data_pwd)

    # пустой token
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await client.post(f"/auth/reset-password/{token}", json=data_pwd)

    # создан email
    assert response.status_code == status.HTTP_200_OK
