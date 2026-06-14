from uuid import UUID

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.schemas.output.user_base import UserBase


class UserActionsService:

    async def read_user(self, user: UUID, db) -> UserBase | None:
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
