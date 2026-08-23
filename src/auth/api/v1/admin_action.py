from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import Body, Depends, Path, status

from src.auth.api.v1.api_router import router
from src.auth.schemas.input.update_schema import UserAdminUpdateSchema
from src.auth.schemas.output.admin_schemas import Users
from src.auth.schemas.output.user_base import UserBase
from src.auth.schemas.output.user_delete import UserDeleted
from src.auth.services.admin_service import AdminActionService
from src.auth.services.user_service import UserActionsService, UserDoesNotExistException
from src.auth.utils.depends import check_admin_user
from src.core.dependencies import get_async_db
from src.auth.exceptions import AuthHTTPException, UserHTTPException
from src.core.exceptions import RepositoryError
from src.core.logger import logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.get(
    "/users",
    dependencies=[Depends(check_admin_user)],
    response_model=Users,
    response_model_exclude={
        "users": {
            "__all__": {
                "is_active",
                "is_staff",
                "is_superuser",
                "full_name",
            }
        }
    },
    status_code=status.HTTP_200_OK,
    name="get_users",
    summary="Admin only. All users.",
    description="""
        Только для администратора. Просмотр списка пользователей.
    """
)
async def get_users(
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> Users:

    try:
        users_data: Users = await AdminActionService().get_all_users(db)
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("register: {}", str(exp))
        AuthHTTPException.raise_http_500()

    return users_data


@router.get(
    "/adm-user/{user_id}",
    dependencies=[Depends(check_admin_user)],
    response_model=UserBase,
    status_code=status.HTTP_200_OK,
    name="get_user_for_admin",
    summary="Данные о пользователе",
    description="""
        Только для администратора. Просмотр информации о пользователе.
    """
)
async def get_user_to_admin(
    user_id: Annotated[UUID, Path(title="id of a user")],
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserBase:

    try:
        user_data: UserBase | None = await UserActionsService().read_user(user_id, db)
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("register: {}", str(exp))
        AuthHTTPException.raise_http_500()
    
    if not user_data:
        UserHTTPException.raise_http_404()

    return user_data


@router.delete(
    "/adm-delete-user/{user_id}",
    response_model=UserDeleted,
    status_code=status.HTTP_200_OK,
    name="admin_delete_user",
    summary="Admin only. Delete user.",
    description="""
        Только для администратора. Удаление пользователя (полное).
    """
)
async def delete_user(
    user_id: Annotated[UUID, Path(title="id of a user")],
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserDeleted:
    
    try:
        user_data: UserDeleted | None = await AdminActionService().delete_user(user_id, db)
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("deleted: {}", str(exp))
        AuthHTTPException.raise_http_500()
    
    if not user_data:
        UserHTTPException.raise_http_404()
    
    return user_data


@router.patch(
    "/adm-update-user/{user_id}",
    dependencies=[Depends(check_admin_user)],
    response_model=UserBase,
    status_code=status.HTTP_200_OK,
    name="admin_update_user",
    summary="Admin only. Update user.",
    description="""
        Изменение данных пользователя администратором. Администратор может менять следующие поля:\n
        
        is_active: bool | None = None
        is_staff: bool | None = None
        is_superuser: bool | None = None
    """
)
async def update_user_admin(
    user_id: UUID,
    update_data: Annotated[UserAdminUpdateSchema, Body()],
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserBase:
    
    try:
        user_data: UserBase | None = await AdminActionService().update_user(user_id, update_data, db)    
    except UserDoesNotExistException:
        UserHTTPException.raise_http_404()
    except RepositoryError:
        AuthHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("admin_update_user: {}", str(exp))
        AuthHTTPException.raise_http_500()
    
    if not user_data:
        UserHTTPException.raise_http_404()
    
    return user_data
