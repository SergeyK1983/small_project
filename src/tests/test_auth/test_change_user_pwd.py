from unittest.mock import patch

import pytest
from src.auth.schemas.output.change_pwd import UserChangePWD
from src.auth.schemas.output.user_base import UserWithPassword


@patch("src.auth.utils.password.UserPasswordRepo.rehash_user_password")
@patch("src.auth.utils.password.UserPasswordRepo.read_user_with_password")
def test_change_user_password(mock_user, mock_change_pwd, client_with_user):
    client, user_factory = client_with_user
   
    mock_user.return_value = UserWithPassword.model_validate(user_factory, from_attributes=True)
    mock_change_pwd.return_value = UserChangePWD.model_validate(user_factory, from_attributes=True)

    form_pwd = {        
        "email": "test_user@example.com",  # зависит от UserFactory
        "password_old": "test_password",
        "password_new": "Qwer12345!",
        "password_rep": "Qwer12345!",
    }

    response = client.patch(
        "/auth/v1/change-password",
        json=form_pwd
    )

    result = response.json()
    assert response.status_code == 200
    assert len(result) == 2
    assert isinstance(result.get("id"), str)
    assert result.get("username") == "test_user"


@patch("src.auth.utils.password.UserPasswordRepo.read_user_with_password")
def test_change_password_none_user(mock_user, client_with_user):
    client, user_factory = client_with_user
   
    mock_user.return_value = None

    form_pwd = {        
        "email": "test_user1@example.com",  # зависит от UserFactory
        "password_old": "test_password",
        "password_new": "Qwer12345!",
        "password_rep": "Qwer12345!",
    }

    response = client.patch(
        "/auth/v1/change-password",
        json=form_pwd
    )

    result = response.json()
    assert response.status_code == 400
    assert result.get("detail") == "The password or email is incorrect."


@pytest.mark.parametrize(
    "form_data, expected",
    [
        (
            {
                "email": "test_user@example.com",
                "password_old": "test_password1",
                "password_new": "Qwer12345!",
                "password_rep": "Qwer12345!"
            },
            "The password or email is incorrect."
        ),
        (
            {
                "email": "test_user@example.com",
                "password_old": "test_password",
                "password_new": "Qwer12345!",
                "password_rep": "Qwer1234!"
            },
            "The passwords you entered don't match"
        ),
    ]
)
@patch("src.auth.utils.password.UserPasswordRepo.read_user_with_password")
def test_change_password_invalid_form_data_pwd(mock_user, client_with_user, form_data, expected):
    client, user_factory = client_with_user
   
    mock_user.return_value = UserWithPassword.model_validate(user_factory, from_attributes=True)

    response = client.patch(
        "/auth/v1/change-password",
        json=form_data
    )

    result = response.json()
    assert response.status_code == 400
    assert result.get("detail") == expected
