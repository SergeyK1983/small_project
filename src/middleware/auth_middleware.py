from typing import Callable

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.auth.utils.depends import authenticate_middleware
from src.auth.utils.token import TypeCookieToken, TypeHeaderToken
from src.core.logger import logger


EXCLUDED_PATHS = {
    "/dev",
    "/auth/v1/signup",
    "/auth/v1/login",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/pay-system/v1/transaction-amount",
    "/pay-system/v1/transaction-webhook",
    "/dev/payment-operation"
}


class AuthMiddleware(BaseHTTPMiddleware):
    """ Аутентификация. Проверка токена в заголовке/куках запроса. """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)
        if "/admin-smp" in request.url.path:
            return await call_next(request)
        if "/static" in request.url.path or "/favicon" in request.url.path:
            return await call_next(request)

        token = None
        if TypeHeaderToken.ACCESS_MIDDLEWARE.value in request.headers:
            token = request.headers[TypeHeaderToken.ACCESS_MIDDLEWARE.value]
        elif TypeCookieToken.ACCESS_MIDDLEWARE.value in request.cookies:
            token = request.cookies[TypeCookieToken.ACCESS_MIDDLEWARE.value]

        if token:
            try:
                await authenticate_middleware(request, token)
            except HTTPException as exp:
                return JSONResponse(status_code=exp.status_code, content={"detail": exp.detail})
            except Exception as exp:
                logger.error("Ошибка сервера: {err}", err=str(exp))
                return JSONResponse(status_code=500, content={"detail": "server error"})
        else:
            return JSONResponse(status_code=401, content={"detail": "Authentication is required"})

        response = await call_next(request)
        return response
