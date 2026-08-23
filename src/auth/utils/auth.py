from typing import TYPE_CHECKING
from uuid import UUID
from fastapi import Request

from src.auth.exceptions import AuthHTTPException, UserHTTPException
from src.auth.repository.black_token_repository import TokenRepo
from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.schemas.output.user_base import UserBase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.utils.token import Payload


class Authentication:
    """ Аутентификация пользователя """

    def __init__(self, request: Request, payload: "Payload"):
        self.request = request
        self.payload = payload
        self.db: "AsyncSession" = request.state.db
        self.request.state.user = None

    async def _authenticate(self) -> None:
        """
        Устанавливает пользователя в Request.state
        Returns:
            None
        """
        user: UserBase | None = await UserRegisteredRepo.read_one_user_by_id(self.payload.uid, self.db)
        if not user:
            UserHTTPException.raise_http_404()
        if not user.is_active:
            AuthHTTPException.raise_http_401()
        self.request.state.user = user
        return None
    
    async def _check_exist_token_black_list(self) -> None:

        jti: UUID = self.payload.jti
        exists: bool = await TokenRepo.is_exists_black_token(jti=jti, db=self.db)

        if exists:
            AuthHTTPException.raise_http_401()
        
        return

    async def is_authenticate(self) -> bool:
        """
        Вернет True или вызовет HTTP ошибку.
        """
        await self._authenticate()
        await self._check_exist_token_black_list()
        return True

