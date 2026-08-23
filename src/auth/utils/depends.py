from typing import Annotated

from fastapi import Depends, Request

from src.auth.exceptions import AuthHTTPException
from .auth import Authentication
from .token import TypeCookieToken, TypeHeaderToken, app_token, Payload


async def authenticate_middleware(request: Request, token: str) -> bool:
    """ Использовать в middleware. Проверяет токен. Устанавливает user: UserBase в request.state.user. """
    
    payload: Payload = app_token.verify_access_token(token)
    auth: bool = await Authentication(request, payload).is_authenticate()    
    return auth


async def get_token_payload(
    token_header: Annotated[str, Depends(TypeHeaderToken.ACCESS.value)],
    token_cookie: Annotated[str, Depends(TypeCookieToken.ACCESS.value)],
) -> Payload:
    """ Вернет полезную нагрузку токена """
    if token_header:
        payload: Payload = app_token.verify_access_token(token_header)
    else:
        payload: Payload = app_token.verify_access_token(token_cookie)
    return payload


async def check_admin_user(request: Request):
    if hasattr(request.state, "user"):
        if request.state.user.is_superuser:
            return True
    AuthHTTPException.raise_http_403()