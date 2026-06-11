from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.repository.user_register_repository import UserRegisterRepo
from src.auth.schemas.input.user_auth_schema import UserSignupSchema

if TYPE_CHECKING:
    from src.auth.schemas.output.user_base import UserBase


class RegistrationServiceException(Exception):
    pass


class RegisterUserAlreadyExists(RegistrationServiceException):
    pass


class RegistrationService:

    def __init__(self, user: UserSignupSchema, db: AsyncSession):
        self.user: UserSignupSchema = user
        self.db_session: AsyncSession = db

    async def create_user(self) -> "UserBase":
        """
        Создает нового пользователя.
        Returns:
            UserBaseSchema data
        """
        user_exists = await UserRegisteredRepo.is_unique_user(
            username=self.user.username,
            email=self.user.email,
            db=self.db_session,
        )

        if user_exists:
            raise RegisterUserAlreadyExists()

        user_created: "UserBase" = await UserRegisterRepo.create_user(
            self.user.username,
            self.user.email,
            self.user.password,
            self.db_session,
        )

        return user_created
