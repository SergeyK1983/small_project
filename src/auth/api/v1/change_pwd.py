from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request, status, Response, Body
from fastapi.responses import JSONResponse

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
    from src.auth.schemas.output.change_pwd import UserChangePWD


@router.patch(
    "/change-password",
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
    body_data: Annotated[UserChangePasswordSchema, Body()],
    db: Annotated["AsyncSession", Depends(get_async_db)],
) -> Response:

    if body_data.password_new != body_data.password_rep:
        AuthHTTPException.raise_http_400()
    
    try:
        body_data.password_new = password.hashing_password(body_data.password_new)

        resp: "UserChangePWD" = await password.change_password(user_id=request.state.user.id, data=body_data, db=db)

        response = JSONResponse(content=resp.model_dump(), status_code=status.HTTP_200_OK)
        response.delete_cookie(key="access_token", httponly=True)
    except (NoneUserModelException, InvalidCredentialsException):
        AuthHTTPException.raise_http_400(
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
    return response
