from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request, status

from src.auth.api.v1.api_router import router
from src.auth.schemas.output.user_base import UserBase
from src.auth.services.user_service import UserActionsService
from src.core.dependencies import get_async_db


from src.auth.exceptions import AuthHTTPException, RepositoryError, UserHTTPException
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.get(
    "/user",
    response_model=UserBase,
    status_code=status.HTTP_200_OK,
    name="get_user",
)
async def get_user(
    request: Request,
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserBase:

    try:
        user_data: UserBase | None = await UserActionsService().read_user(request.state.user.id, db)
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("register: {}", str(exp))
        AuthHTTPException.raise_http_500()
    
    if not user_data:
        UserHTTPException.raise_http_404()

    return user_data

