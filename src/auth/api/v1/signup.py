from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, status

from src.auth.api.v1.api_router import router
from src.core.dependencies import get_async_db
from src.auth.schemas.input.user_auth_schema import UserSignupSchema
from src.auth.schemas.output.user_base import UserBase
from src.auth.services.register_service import RegisterUserAlreadyExists, RegistrationService
from src.auth.utils.password import password
from src.auth.exceptions import AuthHTTPException, RepositoryError
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.post(
    "/signup",
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
    name="signup",
)
async def register(
    user: UserSignupSchema,
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserBase:
    """
    Регистрация пользователя в системе
    Args:
        user: UserAuthSchema - User data
        db: AsyncSession
    Return:
        Registred user data
    """
    
    user.password = password.hashing_password(user.password)
    try:
        response: UserBase = await RegistrationService(
            user=user, db=db
        ).create_user()
    except RegisterUserAlreadyExists:
        AuthHTTPException.raise_http_409()
    except RepositoryError as exp:
        logger.error("register: {}", str(exp))
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("register: {}", str(exp))
        AuthHTTPException.raise_http_500()
    return response
