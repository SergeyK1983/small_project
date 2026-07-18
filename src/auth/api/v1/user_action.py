from typing import TYPE_CHECKING, Annotated

from fastapi import Body, Depends, Request, status

from src.auth.api.v1.api_router import router
from src.auth.schemas.input.update_schema import UserUpdateSchema
from src.auth.schemas.output.user_base import UserBase
from src.auth.schemas.output.user_delete import UserLightDeleted
from src.auth.services.user_service import UserActionsService, UserExistsException
from src.core.dependencies import get_async_db
from src.auth.exceptions import AuthHTTPException, UserHTTPException
from src.core.exceptions import RepositoryError
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


@router.delete(
    "/delete-user",
    response_model=UserLightDeleted,
    status_code=status.HTTP_200_OK,
    name="delete_user",
    description="""
        Мягкое удаление пользователя (is_active=False)
    """
)
async def delete_user(
    request: Request,
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserLightDeleted:
    
    try:
        user_data: UserLightDeleted | None = await UserActionsService().delete_user(request.state.user.id, db)
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("deleted: {}", str(exp))
        AuthHTTPException.raise_http_500()
    
    if not user_data:
        UserHTTPException.raise_http_404()
    
    return user_data


@router.patch(
    "/update-user",
    response_model=UserBase,
    status_code=status.HTTP_200_OK,
    name="update_user",
    description="""
        Изменение данных пользователем. Пользователь может менять следующие поля:\n
        
        username: str | None = None
        email: str | None = None
        first_name: str | None = None
        second_name: str | None = None
        last_name: str | None = None        
    """
)
async def update_user(
    request: Request,
    update_data: Annotated[UserUpdateSchema, Body()],
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserBase:
    
    try:
        user_data: UserBase | None = await UserActionsService().update_user(request.state.user.id, update_data, db)
    except UserExistsException:
        AuthHTTPException.raise_http_409()
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("deleted: {}", str(exp))
        AuthHTTPException.raise_http_500()
    
    if not user_data:
        UserHTTPException.raise_http_404()
    
    return user_data

