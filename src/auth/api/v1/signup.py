from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, status

from src.auth.api.v1.api_router import router
from src.core.dependencies import get_async_db
from src.auth.schemas.user_auth_schema import UserAuthSchema
from src.auth.schemas.user_base_schema import UserBaseSchema
from src.auth.services.register_service import RegisterUserAlreadyExists, RegistrationService
from src.auth.utils.auth import check_admin_user
from src.auth.utils.password import password
from src.auth.exceptions import AuthHTTPException, RepositoryError
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.post(
    "/signup",
    response_model=UserBaseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_admin_user)],
    name="signup",
)
async def register(
    user: UserAuthSchema, db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserBaseSchema:
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
        response: UserBaseSchema = await RegistrationService(
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
