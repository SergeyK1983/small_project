from typing import TYPE_CHECKING
from uuid import UUID

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.schemas.output.user_base import UserBase
from src.auth.schemas.output.user_delete import UserLightDeleted
from src.auth.schemas.input.update_schema import UserUpdateSchema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserServiceException(Exception):
    pass


class UserExistsException(UserServiceException):
    pass


class UserDoesNotExistException(UserServiceException):
    pass

class UserActionsService:

    async def read_user(self, user: UUID, db: "AsyncSession") -> UserBase | None:
        """
        Чтение данных пользователя
        Args:
            user: id of User

        Returns: UserBase data or None
        """
        user_data: UserBase | None = await UserRegisteredRepo.read_one_user_by_id(user, db)
        if user_data is None:
            return None

        return user_data
    
    async def delete_user(self, user: UUID, db: "AsyncSession") -> UserLightDeleted | None:
        """
        Пользователь переводится в "не активные" (мягкое удаление). Флаг **is_active** устанавливается в **False**.
        Args:
            user: id of User

        Returns: UserBase data or None
        """
        data = {"is_active": False}
        user_data: UserBase | None = await UserRegisteredRepo.update_one_user_by_id(user, data, db)
        if user_data is None:
            return None
        
        uld = UserLightDeleted(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            is_active=user_data.is_active
        )
        return uld
    
    async def update_user(self, user_id: UUID, update_data: UserUpdateSchema, db: "AsyncSession") -> UserBase | None:
        """
        Изменение данных пользователя
        Args:
            user: id of User
            update_data: data for update

        Returns: UserBase data or None
        """
        if update_data.username or update_data.email:
            exists: bool = await UserRegisteredRepo.is_unique_user(
                db=db,
                username=update_data.username,
                email=update_data.email
            )
            if exists:
                raise UserExistsException()

        data: dict = update_data.model_dump(exclude_none=True)
        user_data: UserBase | None = await UserRegisteredRepo.update_one_user_by_id(user_id, data, db)
        if user_data is None:
            return None

        return user_data
