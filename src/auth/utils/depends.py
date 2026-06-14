from typing import Annotated

from fastapi import Depends, Request

from src.auth.exceptions import AuthHTTPException
from .auth import Authentication
from .token import TypeHeaderToken, app_token


async def authenticate_middleware(request: Request, token: str) -> bool:
    """ Использовать в middleware. Проверяет токен. Устанавливает user: UserBase в request.state.user. """
    
    payload: dict = app_token.verify_access_token(token)
    auth: bool = await Authentication(request, payload).is_authenticate()    
    return auth


async def get_token_payload(token: Annotated[str, Depends(TypeHeaderToken.ACCESS.value)]) -> dict:
    """ Вернет полезную нагрузку токена """
    
    payload: dict = app_token.verify_access_token(token)
    return payload


async def check_admin_user(request: Request):
    if hasattr(request.state, "user"):
        if request.state.user.is_superuser:
            return True
    AuthHTTPException.raise_http_401()