from typing import TYPE_CHECKING
from uuid import UUID

from src.auth.repository.admin_repository import AdminRepo
from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.schemas.output.admin_schemas import Users
from src.auth.schemas.output.user_base import UserBase
from src.auth.schemas.output.user_delete import UserDeleted
from src.auth.schemas.input.update_schema import UserAdminUpdateSchema

from .user_service import UserDoesNotExistException

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AdminActionService:
    """ Сервис администратора """

    async def get_all_users(self, db: "AsyncSession") -> Users:
        """ Получить список всех пользователей """
        
        users_list: list[UserBase] = await AdminRepo.select_all_users(db)

        users = Users(users=users_list)
        return users
    
    async def delete_user(self, user_id: UUID, db: "AsyncSession") -> UserDeleted | None:
        """
        Удаление данных пользователя
        Args:
            user: id of User

        Returns: UserDeleted data or None
        """
        user_data: UserDeleted | None = await UserRegisteredRepo.delete_user(user_id, db)
        if user_data is None:
            return None

        return user_data
    
    async def update_user(
            self, 
            user_id: UUID, 
            update_data: UserAdminUpdateSchema,
            db: "AsyncSession"
        ) -> UserBase | None:
        """
        Изменение данных пользователя
        Args:
            user: id of User
            update_data: data for update

        Returns: UserBase data or None
        """        
        user: UserBase | None = await UserRegisteredRepo.read_one_user_by_id(user_id, db)
        if not user:
            raise UserDoesNotExistException()

        data: dict = update_data.model_dump(exclude_none=True)
        user_data: UserBase | None = await UserRegisteredRepo.update_one_user_by_id(user_id, data, db)
        if user_data is None:
            return None

        return user_data
