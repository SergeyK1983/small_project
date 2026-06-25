from typing import TYPE_CHECKING
from uuid import UUID

from src.auth.repository.black_token_repository import TokenRepo
from src.auth.repository.user_pwd_repository import UserPasswordRepo
from src.auth.schemas.input.user_auth_schema import UserAuthSchema
from src.auth.schemas.output.token import UserTokenSchema
from src.auth.schemas.output.user_base import UserBase, UserWithPassword
from src.auth.utils.password import password
from src.auth.utils.token import app_token

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.utils.token import Payload


class AuthUserServiceException(Exception):
    pass


class NoneUserModelException(AuthUserServiceException):
    pass


class InvalidCredentialsException(AuthUserServiceException):
    pass


class UserIsNotActiveException(AuthUserServiceException):
    pass


class AuthUserService:

    async def login_user(
        self, user: UserAuthSchema, db: "AsyncSession"
    ) -> UserTokenSchema:

        user_instance: UserWithPassword | None = await UserPasswordRepo.read_user_with_password(
            username=user.username, email=user.email, db=db
        )
        if user_instance is None:
            raise NoneUserModelException()

        verify: bool = password.verify_password(
            hashed=user_instance.password, password=user.password
        )
        if not verify:
            raise InvalidCredentialsException()

        if password.check_rehash_password(hashed_pwd=user_instance.password):
            hashed = password.hashing_password(user.password)
            await UserPasswordRepo.rehash_user_password(user_instance.id, hashed, db)
        
        del user

        if not user_instance.is_active:
            raise UserIsNotActiveException()

        access_token: str = app_token.get_access_token(user_instance.id)
        response = UserTokenSchema(token=access_token, token_type="JWT ")

        return response

    async def logout_user(self, token_payload: "Payload", db: "AsyncSession") -> bool:
        """ Вносит токен пользователя в черный список """
        
        jti: UUID = token_payload.jti
        await TokenRepo.insert_token(jti=jti, db=db)
        
        return True
