from sqlalchemy import select, Select, exists, String, Result
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import RepositoryDatabaseError, RepositoryIntegrityError
from src.auth.models.user import User
from src.core.logger import logger


class UserBaseRepo:

    @staticmethod
    def _select_user_fields() -> Select:
        """Основные данные пользователя"""

        query = select(
            User.id,
            User.username,
            User.email,
            User.is_active,
            User.is_staff,
            User.is_superuser,
            User.first_name,
            User.second_name,
            User.last_name,
        )
        return query

    @staticmethod
    async def _select_execute_query(query: Select, db: AsyncSession) -> Result:
        """Select запрос в БД"""
        try:
            result: Result = await db.execute(query)
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        return result

    @classmethod
    async def _is_exists_user_by_username(cls, username: str, db: AsyncSession) -> bool:
        query: Select = select(exists().where(User.username.cast(String) == username))
        try:
            result: bool = await db.scalar(query)  # type: ignore
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        return result
    
    @classmethod
    async def _is_exists_user_by_email(cls, email: str, db: AsyncSession) -> bool:
        query: Select = select(exists().where(User.email.cast(String) == email))
        try:
            result: bool = await db.scalar(query)  # type: ignore
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        return result
