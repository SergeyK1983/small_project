from typing import TYPE_CHECKING

from fastapi import Request


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    

def get_async_db(request: Request) -> "AsyncSession":
    return request.state.db
