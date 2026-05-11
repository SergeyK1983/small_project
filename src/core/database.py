from asyncio import current_task
from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, async_scoped_session
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


ASYNC_DATABASE_URL = settings.async_postgresql_url
ECHO = settings.ECHO


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self) -> async_scoped_session[AsyncSession]:
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, Any]:
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncGenerator[async_scoped_session[AsyncSession], Any]:
        scoped = self.get_scoped_session()
        try:
            yield scoped
        finally:
            await scoped.remove()
    
    async def dispose(self) -> None:
        await self.engine.dispose()


db_helper = DatabaseHelper(
    url=ASYNC_DATABASE_URL,
    echo=ECHO,
)


class Base(DeclarativeBase):
    pass
