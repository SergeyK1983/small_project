from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, status

from src.auth.api.v1.api_router import router
from src.auth.utils.depends import get_token_payload
from src.core.dependencies import get_async_db
from src.auth.services.auth_service import AuthUserService
from src.auth.exceptions import AuthHTTPException, RepositoryError
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.utils.token import Payload


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
    name="logout",
)
async def logout_user(
    token_payload: Annotated["Payload", Depends(get_token_payload)],
    db: Annotated["AsyncSession", Depends(get_async_db)],
) -> dict:
    """
    Выход пользователя из системы
    Args:
        db: AsyncSession
    """
    
    try:
        await AuthUserService().logout_user(token_payload=token_payload, db=db)
    except RepositoryError as exp:
        logger.error("logout_user RepositoryError: {}", str(exp))
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("logout_user: {}", str(exp))
        AuthHTTPException.raise_http_500()
    return {"msg": "Exit"}
