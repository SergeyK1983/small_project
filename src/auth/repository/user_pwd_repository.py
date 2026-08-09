from uuid import UUID

from sqlalchemy import select, update, String, Select, RowMapping
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas.output.change_pwd import UserChangePWD
from src.core.exceptions import RepositoryDatabaseError, RepositoryError, RepositoryIntegrityError
from src.auth.models.user import User
from src.auth.repository.user_base_repository import UserBaseRepo
from src.auth.schemas.output.user_base import UserWithPassword
from src.core.logger import logger


class UserPasswordRepo(UserBaseRepo):

    @classmethod
    async def read_user_with_password(
        cls, 
        username: str | None,
        email: str | None,
        db: AsyncSession
    ) -> UserWithPassword | None:
        """
        Запрос экземпляра пользователя с паролем. Вернет None, если пользователя нет или не передан username.
        Args:
            username: username of User
            db: AsyncSession
        Return:
            user instance or None
        """

        if username:
            query: Select = cls._get_query_by_username(username)
        elif email:
            query: Select = cls._get_query_by_email(email)
        else:
            return None

        result = await cls._select_execute_query(query, db)
        user_instance = result.scalar_one_or_none()
        if not user_instance:
            return None
        
        user = UserWithPassword.model_validate(user_instance, from_attributes=True)
        return user

    @classmethod
    async def rehash_user_password(
        cls, user_id: UUID, password: str, db: AsyncSession
    ) -> UserChangePWD:
        """
        Обновляет запись пользователя в БД - рехэш пароля.
        Args:
            user_id: id of a user
            password: new password to update user
            db: AsyncSession
        """
        user_data: UserChangePWD = await cls._change_user_password(user_id, password, db)
        if user_data:
            logger.success("Rehash пароля пользователя {}", user_data.username)
        return user_data

    @staticmethod
    def _get_query_by_username(username: str) -> Select:
        query = select(User).where(User.username.cast(String) == username)
        return query
    
    @staticmethod
    def _get_query_by_email(email: str) -> Select:
        query = select(User).where(User.email.cast(String) == email)
        return query

    @classmethod
    async def _change_user_password(
        cls, user_id: UUID, password: str, db: AsyncSession
    ) -> UserChangePWD:
        """
        Обновляет запись пользователя в БД - смена пароля.
        Args:
            user_id: id of a user
            password: new password to update user
            db: AsyncSession
        """
        query = (
            update(User)
            .where(User.id == user_id)
            .values(
                password=password,
            )
            .returning(User.id, User.username)
        )
        try:
            result_returning = await db.execute(query)
            await db.commit()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp

        user_map: RowMapping | None = result_returning.mappings().first()
        if user_map is None:
            raise RepositoryError("User password change error, user must not be None")

        return UserChangePWD(**user_map)
