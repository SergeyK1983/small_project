from typing import Callable

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
