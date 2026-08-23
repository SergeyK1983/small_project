from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import Depends, Path, Request, status

from src.core.dependencies import get_async_db
from src.core.exceptions import ProjectHTTPException, RepositoryError
from src.core.logger import logger
from src.pay_system.api.v1.api_router import router
from src.pay_system.exceptions import PaySystemNotAccountException
from src.pay_system.schemas.output.cash_payment_user import AccountCashPayments
from src.pay_system.services.payment_user_service import CashPaymentUserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.schemas.output.user_base import UserBase


@router.get(
    "/user-cash-payments/{account}",
    response_model=AccountCashPayments,
    status_code=status.HTTP_200_OK,
    name="user_cash_payments",
    summary="Операции по счету",
    description="""
        Перечень операций по указанному счету. Пользователь может просматривать только свои счета. Должен войти
        в систему.
    """
)
async def get_user_cash_account_payments(
    request: Request,
    account: Annotated[UUID, Path(title="account_id")],
    db: Annotated["AsyncSession", Depends(get_async_db)]
):
    user: "UserBase" = request.state.user
    cps = CashPaymentUserService(user, db)
    try:
        payments: AccountCashPayments = await cps.get_user_account_payments(account)
    except PaySystemNotAccountException as exp:
        ProjectHTTPException.raise_http_400(detail=str(exp))
    except RepositoryError:
        ProjectHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("user_cash_payments: {}", str(exp))
        ProjectHTTPException.raise_http_500()
    
    return payments

