from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.repository.user_register_repository import UserRegisterRepo
from src.auth.schemas.user_auth_schema import UserAuthSchema
from src.auth.schemas.user_base_schema import UserBaseSchema


class RegistrationServiceException(Exception):
    pass


class RegisterUserAlreadyExists(RegistrationServiceException):
    pass


class RegistrationService:

    def __init__(self, user: UserAuthSchema, db: AsyncSession):
        self.user: UserAuthSchema = user
        self.db_session: AsyncSession = db

    async def create_user(self) -> UserBaseSchema:
        """
        Создает нового пользователя.
        Returns:
            UserBaseSchema data
        """
        user_exists = await UserRegisteredRepo.is_unique_user(
            username=self.user.username,
            db=self.db_session,
        )

        if user_exists:
            raise RegisterUserAlreadyExists()

        user_fields: dict = await UserRegisterRepo.create_user(
            self.user.username,
            self.user.password,
            self.db_session,
        )

        response = UserBaseSchema(**user_fields)
        return response
