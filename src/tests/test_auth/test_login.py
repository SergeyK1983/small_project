import json
from uuid import uuid4
import pytest_asyncio
import pytest
from unittest.mock import patch
from httpx import Response, ASGITransport, AsyncClient

from src.auth.schemas.output.user_base import UserWithPassword
from src.tests.factories import UserFactory
from src.main import app
from src.core.database import db_helper


# @pytest.mark.asyncio
# async def test_login_user():
#     # user = UserFactory(username="test_user")
#     transport = ASGITransport(app=app)
#     # user = UserFactory(username="test_user").create()
#     UserFactory.create(username="test_user")
#     # session = db_helper.get_scoped_session()
#     # session.add(user)
#     # await session.commit()

#     # await session.flush()

#     # # u = await UserRegisteredRepo.read_one_user_by_username(username="test_user", db=session)
#     # await session.remove()

#     # await add_in_db(user)
#     data = json.dumps({"username": "test_user", "password": "test_password"})

#     async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
#         response: Response = await ac.post(url="/auth/v1/login", json={"username": "test_user", "password": "test_password"})

#     result = response.json()
#     assert response.status_code == 200
#     assert isinstance(result.get("token"), str) is True
#     assert result.get("token_type") == "JWT "

class TestLoginUser:

    @patch("src.auth.services.auth_service.UserPasswordRepo.read_user_with_password")
    def test_login_user_by_username(self, mock_user, client):
        user = UserFactory.build(id=uuid4(), username="test_user")
        mock_user.return_value = UserWithPassword.model_validate(user, from_attributes=True)

        response = client.post(
            "/auth/v1/login",
            json={"username": "test_user", "password": "test_password"}
        )

        result = response.json()
        assert response.status_code == 200
        assert isinstance(result.get("token"), str) is True
        assert result.get("token_type") == "JWT "


    @patch("src.auth.services.auth_service.UserPasswordRepo.read_user_with_password")
    def test_login_user_by_email(self, mock_user, client):
        user = UserFactory.build(id=uuid4(), username="test_user", email="test_user@example.com")
        mock_user.return_value = UserWithPassword.model_validate(user, from_attributes=True)

        response = client.post(
            "/auth/v1/login",
            json={"email": "test_user@example.com", "password": "test_password"}
        )

        result = response.json()
        assert response.status_code == 200
        assert isinstance(result.get("token"), str) is True
        assert result.get("token_type") == "JWT "


    @patch("src.auth.services.auth_service.UserPasswordRepo.read_user_with_password")
    def test_login_user_incorrect_pwd(self, mock_user, client):
        user = UserFactory.build(id=uuid4(), username="test_user")
        mock_user.return_value = UserWithPassword.model_validate(user, from_attributes=True)

        response = client.post(
            "/auth/v1/login",
            json={"username": "test_user", "password": "test_password1"}
        )

        result = response.json()
        assert response.status_code == 401
        assert result.get("detail") == "The password or username is incorrect."


    @patch("src.auth.services.auth_service.UserPasswordRepo.read_user_with_password")
    def test_login_user_not_active_user(self, mock_user, client):
        user = UserFactory.build(id=uuid4(), username="test_user", is_active=False)
        mock_user.return_value = UserWithPassword.model_validate(user, from_attributes=True)

        response = client.post(
            "/auth/v1/login",
            json={"username": "test_user", "password": "test_password"}
        )

        result = response.json()
        assert response.status_code == 403
        assert result.get("detail") == "Access is denied"


    @patch("src.auth.services.auth_service.UserPasswordRepo.read_user_with_password")
    def test_login_user_none_user(self, mock_user, client):
        mock_user.return_value = None

        response = client.post(
            "/auth/v1/login",
            json={"username": "test_user", "password": "test_password1"}
        )

        result = response.json()
        assert response.status_code == 401
        assert result.get("detail") == "The password or username is incorrect."

