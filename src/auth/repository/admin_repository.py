from sqlalchemy import Result, Select, delete, String, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models.user import User
from src.auth.repository.user_base_repository import UserBaseRepo
from src.auth.schemas.output.user_base import UserBase
from src.auth.schemas.output.user_delete import UserDeleted
from src.core.logger import logger


class AdminRepo(UserBaseRepo):
    """Запросы для администратора """

    @classmethod
    async def select_all_users(cls, db: AsyncSession) -> list[UserBase]:
        query: Select = cls._select_user_fields()

        result: Result = await cls._select_execute_query(query, db)
        rows: list[RowMapping] = result.mappings().fetchall() # type: ignore

        users_list = [
            UserBase(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                is_active=row["is_active"],
                is_staff=row["is_staff"],
                is_superuser=row["is_superuser"],
                first_name=row["first_name"],
                second_name=row["second_name"],
                last_name=row["last_name"],
            ) for row in rows if row
        ]
        
        return users_list