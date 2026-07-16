from typing import TYPE_CHECKING, Annotated

from fastapi import Body, Depends, status

from src.auth.utils.depends import check_admin_user
from src.core.dependencies import get_async_db
from src.core.exceptions import ProjectHTTPException, RepositoryError
from src.core.logger import logger
from src.pay_system.api.v1.api_router import router
from src.pay_system.exceptions import PaySystemNotUserException
from src.pay_system.schemas.input.cash_account_user import CashAccountUser
from src.pay_system.schemas.output.cash_account_base import CashAccountBase
from src.pay_system.services.cash_account_service import CashAccountRUBService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession    


@router.post(
    "/create-cash-account",
    dependencies=[Depends(check_admin_user)],
    response_model=CashAccountBase,
    status_code=status.HTTP_201_CREATED,
    name="create_cash_account",
)
async def create_user_cash_account(
    user: Annotated[CashAccountUser, Body],
    db: Annotated["AsyncSession", Depends(get_async_db)]
) -> CashAccountBase:
    
    try:
        response: CashAccountBase = await CashAccountRUBService(user_id=user.user_id, db=db).create_user_cash_account()
    except PaySystemNotUserException:
        ProjectHTTPException.raise_http_404()
    except RepositoryError:
        ProjectHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("create_cash_account: {}", str(exp))
        ProjectHTTPException.raise_http_500()
    return response
