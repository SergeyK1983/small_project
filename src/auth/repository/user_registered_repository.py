from sqlalchemy import Select, delete, String, RowMapping
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models.user import User
from src.auth.repository.user_base_repository import (
    RepositoryDatabaseError, RepositoryIntegrityError, UserBaseRepo,
)
from src.core.logger import logger


class UserRegisteredRepo(UserBaseRepo):
    """Запросы для зарегистрированных пользователей"""

    @classmethod
    async def read_one_user_by_id(cls, user_id: int, db: AsyncSession) -> dict | None:
        query: Select = cls._select_user_fields().where(User.id == user_id)

        result = await cls._select_execute_query(query, db)
        user_map: RowMapping | None = result.mappings().first()
        if user_map is None:
            return None
        return {**user_map}

    @classmethod
    async def read_one_user_by_username(
        cls, username: str, db: AsyncSession
    ) -> dict | None:
        query = cls._select_user_fields().where(User.username.cast(String) == username)

        result = await cls._select_execute_query(query, db)
        user_map: RowMapping | None = result.mappings().first()
        if user_map is None:
            return None
        return {**user_map}

    @classmethod
    async def is_unique_user(cls, username: str, db: AsyncSession) -> bool:
        """
        Проверка на уникальность. Вернет True, если запись с таким username уже существует.
        Args:
            username: str - username
            db: Session
        Returns: True if already exists or False.
        """
        result: bool = await cls._is_exists_user_by_username(username=username, db=db)
        return result

    @classmethod
    async def delete_user(cls, username: str, db: AsyncSession) -> dict | None:
        """
        Удаление записи данных пользователя из БД
        Args:
            user: UserSchema data
            db: Session from get_db()
        """
        query = (
            delete(User)
            .where(
                User.username.cast(String) == username,
            )
            .returning(
                User.username,
            )
        )
        try:
            result = await db.execute(query)
            await db.commit()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp

        user_map: RowMapping | None = result.mappings().first()
        if user_map is None:
            return
        logger.success("Пользователь {} удалён!", username)
        return {**user_map}
