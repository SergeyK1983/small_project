from uuid import uuid4
from unittest.mock import patch

from src.auth.schemas.output.user_base import UserWithPassword
from src.tests.factories import UserFactory


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

