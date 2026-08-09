import pytest

from src.auth.schemas.output.user_base import UserBase

from ..factories import UserFactory


class TestAdminAction:

    @pytest.mark.asyncio
    async def test_full_auth_admin_user(self, db_session, ac_truth):

        uf = UserFactory.build(username="admin", is_superuser=True, is_staff=True)

        db_session.add(uf)
        await db_session.commit()

        user = UserBase.model_validate(uf, from_attributes=True)

        response = await ac_truth.post("/auth/v1/login", json={"username": user.username, "password": "test_password"})
        result = response.json()

        token = "JWT " + result["token"]

        users = UserFactory.build_batch(5)

        db_session.add_all(users)
        await db_session.commit()

        response = await ac_truth.get("/auth/v1/users", headers={"Authorization": token})
        result = response.json()

        assert response.status_code == 200
        assert len(result["users"]) == 6


