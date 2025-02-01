from typing import Callable

from fastapi import status
from httpx import AsyncClient

from schemas.user import UserUpdateSchema


async def test_get_me(client: AsyncClient, authenticate_client: Callable) -> None:
    response = await client.get("/users/me")

    # не авторизован
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client = await authenticate_client(client)
    response = await client.get("/users/me")

    # авторизован
    assert response.status_code == status.HTTP_200_OK


async def test_patch_me(client: AsyncClient, authenticate_client: Callable) -> None:
    user_in = UserUpdateSchema(fullname="New First Name")
    payload = user_in.model_dump(exclude_none=True)
    response = await client.patch("/users/me", json=payload)

    # не авторизован
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client = await authenticate_client(client)
    response = await client.patch("/users/me", json=payload)
    body = response.json()

    # авторизован
    assert response.status_code == status.HTTP_200_OK

    # проверяем правильность обновления
    assert user_in.fullname == body["fullname"]


async def test_get_user(
    client: AsyncClient,
    authenticate_client: Callable,
    test_user_in_db: Callable,
) -> None:
    test_user = await test_user_in_db()
    test_user_id = test_user.get("id")
    response = await client.get(f"/users/{test_user_id}")

    # не авторизован
    assert response.status_code == status.HTTP_200_OK

    client = await authenticate_client(client, is_superuser=True)
    response = await client.get(f"/users/{test_user_id}")
    body_id = response.json()["id"]

    # авторизован
    assert response.status_code == status.HTTP_200_OK

    assert test_user_id == body_id


async def test_patch_user(
    client: AsyncClient,
    authenticate_client: Callable,
    test_user_in_db: Callable,
) -> None:
    test_user = await test_user_in_db()
    test_user_id = test_user.get("id")
    user_in = UserUpdateSchema(fullname="New First Name")
    payload = user_in.model_dump()
    response = await client.patch(f"/users/{test_user_id}", json=payload)

    # не авторизован
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client = await authenticate_client(client)
    response = await client.patch(f"/users/{test_user_id}", json=payload)

    # авторизован, не superuser
    assert response.status_code == status.HTTP_403_FORBIDDEN

    client = await authenticate_client(client, is_superuser=True)
    response = await client.patch(f"/users/{test_user_id}", json=payload)
    body = response.json()

    # авторизован, superuser
    assert response.status_code == status.HTTP_200_OK

    # проверяем правильность обновления
    assert user_in.fullname == body["fullname"]


async def test_del_user(
    client: AsyncClient,
    authenticate_client: Callable,
    test_user_in_db: Callable,
) -> None:
    test_user = await test_user_in_db()
    test_user_id = test_user.get("id")
    response = await client.delete(f"/users/{test_user_id}")

    # не авторизован
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    client = await authenticate_client(client)
    response = await client.delete(f"/users/{test_user_id}")

    # авторизован, не superuser
    assert response.status_code == status.HTTP_403_FORBIDDEN

    client = await authenticate_client(client, is_superuser=True)
    response_del = await client.delete(f"/users/{test_user_id}")

    # авторизован, superuser
    assert response_del.status_code == status.HTTP_200_OK

    response_get = await client.get(f"/users/{test_user_id}")

    # ищем удаленный объект
    assert response_get.status_code != status.HTTP_200_OK


async def test_list_users(
    client: AsyncClient,
    registered_user: Callable,
    batch_test_user_in_db: Callable,
) -> None:
    await batch_test_user_in_db()
    response = await client.get("/users/")
    data = response.json()["page_data"]

    assert response.status_code == status.HTTP_200_OK

    assert len(data) > 9

    email = "example@test.com"
    await registered_user(client, email=email)
    response = await client.get("/users/", params={"email": email})
    data = response.json()["page_data"]

    assert response.status_code == status.HTTP_200_OK

    assert len(data) > 0

    email = "mhgnfbv@jhngbv.jmhngbv"
    response = await client.get("/users/", params={"email": email})

    assert response.status_code == status.HTTP_404_NOT_FOUND
