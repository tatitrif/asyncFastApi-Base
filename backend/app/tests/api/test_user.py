from unittest import IsolatedAsyncioTestCase

from fastapi import status
from httpx import ASGITransport, AsyncClient

from core.session_manager import db_manager
from main import app
from tests import test_settings

transport = ASGITransport(app=app)
BASE_URL = f"http://127.0.0.1:8000{test_settings.API_V1_STR}"


class UserTest(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        db_manager.init(
            test_settings.SQLALCHEMY_DATABASE_URI, {"echo": True, "future": True}
        )

    async def asyncSetUp(self):
        await db_manager.drop_all()
        await db_manager.create_all()
        self.client = AsyncClient(transport=transport, base_url=BASE_URL)
        self.user_data = {
            "username": "username1",
            "email": "username1@example.com",
            "fullname": "string",
            "password": "password",
            "confirmation_password": "password",
        }
        response = await self.client.post("/auth/signup", json=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user_id = response.json()["id"]

    async def asyncTearDown(self):
        await db_manager.drop_all()
        await self.client.aclose()

    async def test_list_users(self):
        response = await self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIsInstance(data["page_data"], list)

    async def test_find_users(self):
        find_email = self.user_data["email"]
        response = await self.client.get("/users/", params={"email": find_email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["page_data"][0]
        self.assertEqual(data["email"], find_email)

    async def test_unauthorized_update_del_users(self):
        users_update = {"fullname": "change fullname"}

        response = await self.client.patch(f"/users/{self.id}", json=users_update)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = await self.client.delete(f"/users/{self.id}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
