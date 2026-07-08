from sqlalchemy import String, RowMapping, Insert
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RepositoryDatabaseError, RepositoryError, RepositoryIntegrityError
from src.auth.models.user import User
from src.auth.repository.user_base_repository import UserBaseRepo
from src.auth.schemas.output.user_base import UserBase

from src.core.logger import logger


class UserRegisterRepo(UserBaseRepo):
    """Для регистрации пользователя"""

    @classmethod
    async def __create(cls, username: str, query: Insert, db: AsyncSession) -> UserBase:
        try:
            await db.execute(query)
            await db.commit()

            result = await db.execute(
                cls._select_user_fields().where(User.username.cast(String) == username)
            )
            user_created: RowMapping | None = result.mappings().first()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp

        if user_created is None:
            raise RepositoryError("User create error, user must not be None")

        logger.success("Пользователь {name} зарегистрирован!", name=username)
        return UserBase(**user_created)

    @classmethod
    async def create_user(cls, username: str, email: str, password: str, db: AsyncSession) -> UserBase:
        """
        Запрос на создание пользователя.
        Args:
            username: username of user
            email: email of user
            db: AsyncSession
        Returns:
            created user's dict fields
        """
        query = insert(User).values(
            username=username,
            email=email,
            password=password,
            is_active=True
        )
        result: UserBase = await cls.__create(username, query, db)
        return result

    @classmethod
    async def create_superuser(cls, username: str, email: str, password: str, db: AsyncSession) -> UserBase:
        """
        Запрос на создание суперпользователя.
        Args:
            username: username of user
            email: email of user
            db: AsyncSession
        Returns:
            created user's dict fields
        """
        query = insert(User).values(
            username=username,
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        result: UserBase = await cls.__create(username, query, db)
        return result
