import pytest
from uuid import uuid4
from unittest.mock import patch

from src.auth.schemas.output.user_base import UserBase
from src.tests.factories import UserFactory


class TestSignup:

    @patch("src.auth.services.register_service.UserRegisteredRepo.is_unique_user")
    @patch("src.auth.services.register_service.UserRegisterRepo.create_user")
    def test_signup_user_create(self, mock_user, mock_is_user, client):
        user = UserFactory.build(id=uuid4(), username="test_user")

        mock_is_user.return_value = False
        mock_user.return_value = UserBase.model_validate(user, from_attributes=True)

        data = {
            "username": "test_user",
            "email": "test_user@example.com",  # зависит от UserFactory
            "password": "Qwer1234!"
        }

        response = client.post(
            "/auth/v1/signup",
            json=data
        )

        result = response.json()
        assert response.status_code == 201
        assert len(result) == 10
        assert result.get("username") == "test_user"
        assert result.get("email") == "test_user@example.com"
        assert result.get("is_active") == True
        assert result.get("is_staff") == False
        assert result.get("is_superuser") == False


    @patch("src.auth.services.register_service.UserRegisteredRepo.is_unique_user")
    def test_signup_user_raise_409(self, mock_is_user, client):
        mock_is_user.return_value = True

        data = {
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "Qwer1234!"
        }

        response = client.post(
            "/auth/v1/signup",
            json=data
        )

        result = response.json()
        assert response.status_code == 409    
        assert result.get("detail") == "A user with this username or email already exists"
        

    @pytest.mark.parametrize(
        "form_data, field, expected",
        [
            ({"email": "test_user@example.com", "password": "Qwer1234!"}, "username", "Field required" ),
            ({"username": "test_user", "password": "Qwer1234!"}, "email", "Field required" ),
            ({"username": "test_user", "email": "test_user@example.com"}, "password", "Field required" ),
        ]
    )
    def test_signup_user_invalid_form(self, client, form_data, field, expected):
        
        response = client.post(
            "/auth/v1/signup",
            json=form_data
        )

        result = response.json()
        assert response.status_code == 422
        assert result.get("detail")[0].get("loc")[1] == field
        assert result.get("detail")[0].get("msg") == expected


    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                {"username": "use", "email": "test_user@example.com", "password": "Qwer1234!"}, 
                "Value should have at least 4 items after validation, not 3"
            ),
            (
                {"username": "useфыв", "email": "test_user@example.com", "password": "Qwer1234!"},
                "Value error, Username can only contain Latin letters, numbers, and _"
            ),
            (
                {"username": "user", "email": "test_example.com", "password": "Qwer1234!"},
                "value is not a valid email address: An email address must have an @-sign."
            ),
            (
                {"username": "user", "email": "test_user@example.com", "password": "Qwer123"},
                "Value error, Пароль должен состоять минимум из 8 символов / Должен содержать хотя бы " +
                "один спецсимвол ! @ # $ % ^ & * ( )"
            ),
        ]
    )
    def test_signup_user_invalid_data(self, client, data, expected):
        
        response = client.post(
            "/auth/v1/signup",
            json=data
        )

        result = response.json()
        assert response.status_code == 422
        assert result.get("detail")[0].get("msg") == expected
