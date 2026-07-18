from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import Depends, Path, status

from src.auth.utils.depends import check_admin_user
from src.core.dependencies import get_async_db
from src.core.exceptions import ProjectHTTPException, RepositoryError
from src.core.logger import logger
from src.pay_system.api.v1.api_router import router
from src.pay_system.schemas.output.cash_account_user import UserCashAccounts
from src.pay_system.services.account_admin_service import CashAccountAdminService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@router.get(
    "/adm-cash-accounts-user/{user_id}",
    dependencies=[Depends(check_admin_user)],
    response_model=UserCashAccounts,
    response_model_exclude={
        "accounts": {
            "__all__": {
                "id",
                "created",
                "updated",
                "user_id",
            }
        }
    },
    status_code=status.HTTP_200_OK,
    name="adm_cash_accounts_user",
    summary="Admin only. Счета",
    description="""
        Просмотр администратором счетов пользователя и их балансов.

        user_id: UUID
    """
)
async def get_cash_accounts_user(
    user_id: Annotated[UUID, Path(title="id of a user")],
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> UserCashAccounts:
    try:
        accounts: UserCashAccounts = await CashAccountAdminService(user_id, db).get_user_accounts()
    
    except RepositoryError:
        ProjectHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("adm_cash_accounts_user: {}", str(exp))
        ProjectHTTPException.raise_http_500()
    
    return accounts
