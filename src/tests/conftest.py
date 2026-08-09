from typing import Any, AsyncGenerator, Generator
from unittest.mock import patch
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.datastructures import State
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine

from src.auth.schemas.output.user_base import UserBase
from src.core.config import settings
from src.core.database import Base, DatabaseHelper
from src.main import app
from src.auth.models import *
from src.pay_system.models import *

from .factories import UserFactory


TEST_DATABASE_URL = settings.async_test_postgresql_url


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app, base_url="http://localhost")
    return client


@pytest.fixture
def client_with_user(monkeypatch) -> Generator[tuple[TestClient, UserFactory]]:
    """ Фикстура для клиента с авторизованным пользователем """

    uf = UserFactory.build(id=uuid4(), username="test_user")
    user = UserBase.model_validate(uf, from_attributes=True)
    
    with patch("src.middleware.auth_middleware.authenticate_middleware") as mock_auth:
        mock_auth.return_value = True
        monkeypatch.setattr(State, "user", user, raising=False)

        client = TestClient(app, base_url="http://localhost", headers={"Authorization": "JWT tratata"})
        yield client, uf


#============== БД ================

from sqlalchemy.pool import NullPool


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """ Движок на все тесты """

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        # pool_pre_ping=False,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_connection(test_engine) -> AsyncGenerator[AsyncConnection, Any]:
    """ Transaction per test """

    connection = await test_engine.connect()

    transaction = await connection.begin()

    try:
        yield connection

    finally:
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def db_session(db_connection: AsyncConnection) -> AsyncGenerator[AsyncSession, Any]:
    """ Session for tests """

    session_factory = async_sessionmaker(
        bind=db_connection,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_db_helper(db_connection: AsyncConnection):
    """ Test DatabaseHelper """

    helper = DatabaseHelper(
        url=TEST_DATABASE_URL,
        echo=False,
    )

    helper.session_factory = async_sessionmaker(
        bind=db_connection,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    # Engine самого helper здесь больше не нужен
    await helper.engine.dispose()

    return helper


@pytest_asyncio.fixture
async def mocked_db_middleware(test_db_helper, monkeypatch):
    """ Replace DatabaseHelper used by middleware """

    monkeypatch.setattr("src.core.middleware.db_helper", test_db_helper)

    yield test_db_helper

# =========================================================


@pytest_asyncio.fixture
async def ac(mocked_db_middleware) -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app)    

    with patch("src.middleware.auth_middleware.authenticate_middleware") as mock_auth:
        mock_auth.return_value = True

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            headers={"Authorization": "JWT tratata"},
        ) as async_client:

            yield async_client


@pytest_asyncio.fixture
async def ac_truth(mocked_db_middleware) -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as async_client:

        yield async_client


@pytest_asyncio.fixture 
async def create_user(db_session) -> UserBase:
    """ Создает одного пользователя в БД """

    uf = UserFactory.build()

    db_session.add(uf)
    await db_session.commit()

    user = UserBase.model_validate(uf, from_attributes=True)

    return user

