from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request, status

from src.core.dependencies import get_async_db
from src.core.exceptions import ProjectHTTPException, RepositoryError
from src.core.logger import logger
from src.pay_system.api.v1.api_router import router
from src.pay_system.schemas.output.cash_account_user import UserCashAccounts
from src.pay_system.services.account_user_service import CashAccountUserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.schemas.output.user_base import UserBase


@router.get(
    "/user-cash-accounts",
    response_model=UserCashAccounts,
    status_code=status.HTTP_200_OK,
    name="user_cash_accounts",
    description="""
        Счета пользователя
    """
)
async def get_user_cash_accounts(
    request: Request,
    db: Annotated["AsyncSession", Depends(get_async_db)]
):
    user: "UserBase" = request.state.user
    try:
        accounts: UserCashAccounts = await CashAccountUserService(user, db).get_user_accounts()
    
    except RepositoryError:
        ProjectHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("user_cash_accounts: {}", str(exp))
        ProjectHTTPException.raise_http_500()
    
    return accounts
