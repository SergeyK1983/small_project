from uuid import uuid4

import pytest
from fastapi.datastructures import State

from src.auth.models.user import User


class TestUserActions:

    @pytest.mark.asyncio
    async def test_get_user(self, create_user, ac, monkeypatch):
        
        user = create_user
        monkeypatch.setattr(State, "user", user, raising=False)  # как бы прошел аутентификацию

        response = await ac.get("/auth/v1/user")
        result = response.json()

        assert response.status_code == 200
        assert result["username"] == user.username
        assert result["email"] == user.email

    @pytest.mark.asyncio
    async def test_get_another_user(self, create_user, ac, monkeypatch):

        user = create_user
        user.id = uuid4()

        # прошел аутентификацию, но это уже другой пользователь
        monkeypatch.setattr(State, "user", user, raising=False)

        response = await ac.get("/auth/v1/user")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user(self, db_session, create_user, ac, monkeypatch):

        user = create_user
        monkeypatch.setattr(State, "user", user, raising=False)

        obj = await db_session.get(User, user.id)

        assert obj.is_active is True

        response = await ac.delete("/auth/v1/delete-user")
        result = response.json()

        assert response.status_code == 200
        assert result["id"] == str(user.id)
        assert result["is_active"] == False

        user.id = uuid4()
        monkeypatch.setattr(State, "user", user, raising=False)
        response = await ac.delete("/auth/v1/delete-user")

        assert response.status_code == 404
        
