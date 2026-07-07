from typing import TYPE_CHECKING
from uuid import UUID

from src.auth.exceptions import InvalidCredentialsException, NoneUserModelException
from src.auth.repository.user_pwd_repository import UserPasswordRepo
from src.auth.utils.hasher import hasher


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.utils.hasher import Argon2Hasher
    from src.auth.schemas.input.change_pwd_schema import UserChangePasswordSchema
    from src.auth.schemas.output.user_base import UserWithPassword


class Password:

    def __init__(self, hasher: "Argon2Hasher"):
        self.hasher = hasher

    def hashing_password(self, pwd: str) -> str:        
        hash_pwd: str = self.hasher.hashing_password(password=pwd)
        return hash_pwd

    def verify_password(self, hashed: str, password: str) -> bool:
        verify: bool = self.hasher.verify(hashed=hashed, password=password)
        return verify

    def check_rehash_password(self, hashed_pwd: str) -> bool:
        return self.hasher.needs_rehash(hashed_pwd)

    async def change_password(self, user_id: UUID, data: "UserChangePasswordSchema", db: "AsyncSession"):
        """ Смена пароля """

        user_pwd: "UserWithPassword | None" = await UserPasswordRepo.read_user_with_password(
            username=None, email=data.email, db=db
        )
        if user_pwd is None:
            raise NoneUserModelException()

        verify: bool = self.verify_password(
            hashed=user_pwd.password, password=data.password_old
        )
        if not verify:
            raise InvalidCredentialsException()
        
        resp: dict = await UserPasswordRepo.rehash_user_password(
            user_id=user_id, password=data.password_new, db=db
        )
        return resp

    def reset_password(self): ...


password = Password(hasher)
