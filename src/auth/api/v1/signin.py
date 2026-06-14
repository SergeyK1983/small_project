from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, status, Response

from src.auth.api.v1.api_router import router
from src.auth.schemas.input.user_auth_schema import UserAuthSchema
from src.auth.schemas.output.token import UserTokenSchema
from src.auth.utils.hasher import HasherError
from src.core.dependencies import get_async_db
from src.auth.services.auth_service import (
    AuthUserService, InvalidCredentialsException, NoneUserModelException, UserIsNotActiveException
)

from src.auth.exceptions import AuthHTTPException
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.post(
    "/login",
    response_model=UserTokenSchema,
    status_code=status.HTTP_200_OK,
    name="login",
)
async def login_user(
    response: Response,
    user_data: UserAuthSchema,
    db: Annotated["AsyncSession", Depends(get_async_db)],
) -> UserTokenSchema:
    """
    Вход пользователя в систему
    Args:
        user_data: User data (username, email, password)
        db: AsyncSession
    Return:
        User token
    """
    
    try:
        resp: UserTokenSchema = await AuthUserService().login_user(user=user_data, db=db)

        response.set_cookie(
            key="access_token",
            value=(resp.token_type + resp.token),
            httponly=True
        )

    except (NoneUserModelException, InvalidCredentialsException):
        AuthHTTPException.raise_http_401(
            detail="The password or username is incorrect."
        )
    except UserIsNotActiveException:
        AuthHTTPException.raise_http_403()
    except HasherError as exp:
        logger.error("login_user: {}", str(exp))
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("login_user: {}", str(exp))
        AuthHTTPException.raise_http_500()
    return resp
