from fastapi.testclient import TestClient
import pytest_asyncio
import pytest
from typing import TYPE_CHECKING, Any, AsyncGenerator
from httpx import ASGITransport, AsyncClient

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


@pytest_asyncio.fixture
async def add_in_db() -> None:
    user = UserFactory(username="test_user")
    session = db_helper.async_scoped_session()
    session.add(user)
    await session.flush()
    return
