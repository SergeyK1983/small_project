from typing import Annotated, TYPE_CHECKING
from uuid import UUID, uuid4
from fastapi import Request, Depends

from src.auth.exceptions import AuthHTTPException, UserHTTPException
from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.auth.schemas.output.user_base import UserBase
from src.auth.utils.token import TypeHeaderToken, app_token

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Authentication:
    def __init__(self, request: Request, payload: dict):
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
        user: UserBase | None = await UserRegisteredRepo.read_one_user_by_id(self.payload.get("uid", 0), self.db)
        if not user:
            UserHTTPException.raise_http_404()
        self.request.state.user = user
        return None
    
    async def _check_exist_token_black_list(self):
        jti: UUID = self.payload.get("jti", uuid4())

        user = self.request.state.user
        cache_token_jti = ""

        if user.username and hasattr(self.request.app.state, "redis_client"):
            pass
        
        if cache_token_jti and cache_token_jti == str(jti):
            AuthHTTPException.raise_http_401()
        return

    async def is_authenticate(self) -> bool:
        """
        Вернет True или вызовет HTTP ошибку.
        """
        await self._authenticate()
        await self._check_exist_token_black_list()
        return True

