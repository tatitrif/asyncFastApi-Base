from unittest import IsolatedAsyncioTestCase

from fastapi import status
from fastapi.testclient import TestClient

from core.session_manager import db_manager
from main import app
from services.auth import AuthService
from services.helpers.security import verify_pwd
from tests import test_settings

BASE_URL = f"http://127.0.0.1:8000{test_settings.API_V1_STR}"


class AuthTest(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        db_manager.init(
            test_settings.SQLALCHEMY_DATABASE_URI, {"echo": True, "future": True}
        )
        cls.client = TestClient(app, base_url=BASE_URL)

    async def asyncSetUp(self):
        await self.asyncTearDown()
        await db_manager.create_all()

    async def asyncTearDown(self):
        await db_manager.drop_all()

    async def test_register_user_user(self):
        user_data = {
            "username": "username1",
            "email": "username1@example.com",
            "fullname": "string",
            "password": "password",
            "confirmation_password": "password",
        }
        response = self.client.post("/auth/signup", json=user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_id = response.json()["id"]
        response = self.client.get(f"/users/{user_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["email"], "username1@example.com")

        # Проверим, что пароль зашифрован
        async with db_manager.session() as session:
            user = await AuthService(session)._identification_by_username(
                username="username1"
            )
        self.assertNotEqual(user.hashed_password, user_data["password"])
        self.assertTrue(verify_pwd(user_data["password"], user.hashed_password))

    def test_register_user_duplicate(self):
        """Попытка зарегистрировать уже существующего пользователя"""
        user_data = {
            "username": "username1",
            "email": "username1@example.com",
            "fullname": "string",
            "password": "password",
            "confirmation_password": "password",
        }
        response = self.client.post("/auth/signup", json=user_data)
        self.assertNotEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_register_user_empty_password(self):
        """Пустой пароль"""
        user_data = {
            "username": "username3",
            "email": "username3@example.com",
            "fullname": "string",
            "password": "",
            "confirmation_password": "string",
        }
        response = self.client.post("/auth/signup", json=user_data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_empty(self):
        """Без данных"""
        user_data = {}
        response = self.client.post("/auth/signup", json=user_data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
