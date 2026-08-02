from unittest.mock import patch
from uuid import uuid4
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.datastructures import State
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from src.auth.schemas.output.user_base import UserBase
from src.main import app
from src.core.database import db_helper

from .factories import UserFactory


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from factory.base import Factory


@pytest_asyncio.fixture
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as async_client:
        yield async_client


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app, base_url="http://localhost")
    return client


@pytest.fixture
def client_with_user(monkeypatch) -> Generator[tuple[TestClient, UserFactory]]:
    uf = UserFactory.build(id=uuid4(), username="test_user")
    user = UserBase.model_validate(uf, from_attributes=True)
    
    with patch("src.middleware.auth_middleware.authenticate_middleware") as mock_auth:
        mock_auth.return_value = True
        monkeypatch.setattr(State, "user", user, raising=False)

        client = TestClient(app, base_url="http://localhost", headers={"Authorization": "JWT tratata"})
        yield client, uf


@pytest_asyncio.fixture
async def add_in_db() -> None:
    user = UserFactory(username="test_user")
    session = db_helper.async_scoped_session()
    session.add(user)
    await session.flush()
    return
