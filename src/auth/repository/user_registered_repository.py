from uuid import UUID

from sqlalchemy import Result, Select, delete, String, RowMapping, exists, select, update, and_
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models.user import User
from src.auth.repository.user_base_repository import UserBaseRepo
from src.core.exceptions import RepositoryDatabaseError, RepositoryIntegrityError
from src.auth.schemas.output.user_base import UserBase
from src.auth.schemas.output.user_delete import UserDeleted
from src.core.logger import logger


class UserRegisteredRepo(UserBaseRepo):
    """Запросы для зарегистрированных пользователей"""

    @classmethod
    async def read_one_user_by_id(cls, user_id: UUID, db: AsyncSession) -> UserBase | None:
        query: Select = cls._select_user_fields().where(User.id == user_id)

        result = await cls._select_execute_query(query, db)
        user_map: RowMapping | None = result.mappings().first()
        if user_map is None:
            return None
        return UserBase(**user_map)

    @classmethod
    async def read_one_user_by_username(cls, username: str, db: AsyncSession) -> UserBase | None:
        query = cls._select_user_fields().where(User.username.cast(String) == username)

        result = await cls._select_execute_query(query, db)
        user_map: RowMapping | None = result.mappings().first()
        if user_map is None:
            return None
        return UserBase(**user_map)
    
    @classmethod
    async def read_one_user_by_email(cls, email: str, db: AsyncSession) -> UserBase | None:
        query = cls._select_user_fields().where(User.email.cast(String) == email)

        result = await cls._select_execute_query(query, db)
        user_map: RowMapping | None = result.mappings().first()
        if user_map is None:
            return None
        return UserBase(**user_map)

    @classmethod
    async def is_unique_user(cls, db: AsyncSession, username: str | None = None, email: str | None = None) -> bool:
        """
        Проверка на уникальность. Вернет True, если запись с таким username или email уже существует.
        Поднимет исключение ValueError, если не передан ни один из аргументов: username и email.
        Args:
            username: str | None - username of user
            email: str | None - email of user
            db: AsyncSession
        Returns: True if already exists or False.
        """
        
        if username and email:
            is_username: bool = await cls._is_exists_user_by_username(username=username, db=db)
            is_email: bool = await cls._is_exists_user_by_email(email=email, db=db)
            return is_username or is_email
        
        if username:
            result: bool = await cls._is_exists_user_by_username(username=username, db=db)
            return result
        
        if email:
            result: bool = await cls._is_exists_user_by_email(email=email, db=db)
            return result
        
        if not username and not email:
            raise ValueError("is_unique_user: username and email at least one must be passed")
    
    @classmethod
    async def is_exists_user_by_id(cls, user_id: UUID, db: AsyncSession) -> bool:
        """ Вернет True, если пользователь существует, иначе False """

        query: Select = select(exists().where(User.id == user_id))     
        
        result: Result = await cls._select_execute_query(query, db)
        is_exists: bool = result.scalar() # type: ignore
        return is_exists
    
    @classmethod
    async def is_exists_and_active_user_by_id(cls, user_id: UUID, db: AsyncSession) -> bool:
        """ Вернет True, если пользователь существует и активен, иначе False """

        query: Select = select(exists().where(and_(User.id == user_id, User.is_active == True)))     
        
        result: Result = await cls._select_execute_query(query, db)
        is_exists: bool = result.scalar() # type: ignore
        return is_exists

    @classmethod
    async def delete_user(cls, user_id: UUID, db: AsyncSession) -> UserDeleted | None:
        """
        Удаление записи данных пользователя из БД. Вернет UserDeleted, если пользователь был удалён.
        Args:
            user_id: UUID - id of user
            db: AsyncSession
        """
        query = (
            delete(User)
            .where(
                User.id == user_id,
            )
            .returning(
                User.id,
                User.username,
                User.email,
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
        logger.success("Пользователь {} удалён!", user_id)
        return UserDeleted(**user_map)
    
    @classmethod
    async def update_one_user_by_id(cls, user_id: UUID, data: dict, db: AsyncSession) -> UserBase | None:
        """
        Изменение данных записи о пользователе в БД. Вернет pydantic модель UserBase, если если данные изменены или 
        None.
        Args:
            user_id: id of user
            data: data for update
            db: AsyncSession

        Returns: RowMapping user data
        """
        query = (
            update(
                User
            ).
            where(
                User.id == user_id
            ).
            returning(
                User
            )
        )

        try:
            result = await db.execute(query, data)
            await db.commit()
        except IntegrityError as exp:
            logger.error("Ошибка изменения данных пользователя из БД {}", exp)
            return

        user_map: RowMapping | None = result.mappings().first()
        
        if user_map is None:
            return None
        logger.success("Данные пользователя id - {} изменены", user_id)
        
        return UserBase.model_validate(user_map["User"], from_attributes=True)
