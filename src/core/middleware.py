import time
import uuid
from typing import Callable

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.database import db_helper


class DBSessionMiddleware(BaseHTTPMiddleware):
    """ Одна сессия на все запросы """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        async with db_helper.session_factory() as session:
            request.state.db = session
            response = await call_next(request)

        return response


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.perf_counter()

        request_id = str(uuid.uuid4())

        user_id = "-"
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", "-")

        client_ip = request.client.host if request.client else "-"

        method = request.method
        path = request.url.path

        try:
            with logger.contextualize(
                request_id=request_id,
                user_id=user_id,
                method=method,
                path=path,
                client_ip=client_ip,
                status_code="-",
                execution_time_ms="-",
            ):

                response = await call_next(request)

                execution_time = round((time.perf_counter() - start_time) * 1000, 2)

                with logger.contextualize(
                    request_id=request_id,
                    user_id=user_id,
                    method=method,
                    path=path,
                    client_ip=client_ip,
                    status_code=response.status_code,
                    execution_time_ms=execution_time,
                ):
                    logger.info("Request completed")

                response.headers["X-Request-ID"] = request_id
                return response

        except Exception:
            execution_time = round((time.perf_counter() - start_time) * 1000, 2)

            with logger.contextualize(
                request_id=request_id,
                user_id=user_id,
                method=method,
                path=path,
                client_ip=client_ip,
                status_code=500,
                execution_time_ms=execution_time,
            ):
                logger.exception("Request failed")

            raise
