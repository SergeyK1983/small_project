from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request, status, Response, Body

from src.auth.api.v1.api_router import router
from src.auth.schemas.input.change_pwd_schema import UserChangePasswordSchema
from src.auth.utils.password import password
from src.auth.utils.hasher import HasherError
from src.core.dependencies import get_async_db
from src.auth.exceptions import AuthHTTPException, InvalidCredentialsException, NoneUserModelException
from src.core.exceptions import RepositoryError
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.patch(
    "/change-password",
    status_code=status.HTTP_200_OK,
    name="change_password",
    description="""
        Смена пароля пользователем. Фронт должен выполнить logout.\n
        
        email: str
        password_old: str
        password_new: str
        password_rep: str
    """
)
async def change_user_password(
    request: Request,
    body_data: Annotated[UserChangePasswordSchema, Body],
    db: Annotated["AsyncSession", Depends(get_async_db)],
) -> Response:

    if body_data.password_new != body_data.password_rep:
        AuthHTTPException.raise_http_400()
    
    try:
        body_data.password_new = password.hashing_password(body_data.password_new)

        resp: dict = await password.change_password(user_id=request.state.user.id, data=body_data, db=db)

    except (NoneUserModelException, InvalidCredentialsException):
        AuthHTTPException.raise_http_401(
            detail="The password or email is incorrect."
        )    
    except HasherError as exp:
        logger.error("change_password: {}", str(exp))
        AuthHTTPException.raise_http_500()
    except RepositoryError as exp:
        logger.error("change_password: {}", str(exp))
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("change_password: {}", str(exp))
        AuthHTTPException.raise_http_500()
    return Response(content=f"Пароль изменён, пользователь {resp["id"]}")
