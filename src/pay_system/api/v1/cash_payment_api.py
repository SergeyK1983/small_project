import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from aiohttp import ClientSession, ClientTimeout, ClientResponseError, ClientError
from fastapi import Body, Depends, status, Query, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.core.dependencies import get_async_db
from src.core.exceptions import ProjectHTTPException, RepositoryError
from src.core.logger import logger
from src.pay_system.api.v1.api_router import router
from src.pay_system.exceptions import (
    PaySystemBalanceLessZeroException, PaySystemNotAccountException, PaySystemNotUserException, 
    PaySystemPaymentException
)
from src.pay_system.schemas.input.cash_payment_webhook import Amount, CashPaymentSchema, CashPaymentWebhook
from src.pay_system.schemas.output.account_payment import CashAccountPayment
from src.pay_system.services.cash_account_service import CashAccountRUBService
from src.pay_system.services.cash_payment_service import CashPaymentRUBService
from src.pay_system.services.payment_webhook import ThirdPaymentSystem

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase
    from src.pay_system.schemas.output.cash_payment_base import CashPaymentBase


PATH_SEND = "http://localhost:8010/pay-system/v1/"


@router.get(
    "/transaction-amount",
    name="amount",
)
async def transaction_amount(    
    db: Annotated["AsyncSession", Depends(get_async_db)],
    amount: Annotated[str, Query()],
    account_id: Annotated[str, Query()],
) -> Response:
    
    try:
        cash_amount = Amount(amount=amount, account_id=account_id) # type: ignore
    except ValidationError as exp:
        logger.error("transaction_amount: {}", str(exp))
        ProjectHTTPException.raise_http_400(detail=f"Переданы некорректные данные, проверьте: {amount=}, {account_id=}")    
    
    th_payment_system = ThirdPaymentSystem(db)
    
    try:
        cash_account: CashAccountBase = await th_payment_system.check_account_id(cash_amount.account_id)

        cash_payment: CashPaymentWebhook = th_payment_system.prepare_data_webhook(
            amount=cash_amount.amount,
            account_id=cash_amount.account_id,
            user_id=cash_account.user_id
        )
        timeout = ClientTimeout(total=4)
        async with ClientSession(base_url=PATH_SEND, timeout=timeout) as session:
            data = cash_payment.model_dump()
            try:
                async with session.post("transaction-webhook", json=data) as response:  # application/json auto
                    status_: int = response.status
                    message = await response.json()
            except asyncio.exceptions.TimeoutError:
                currently = datetime.now()
                logger.error("TimeoutError, {}", currently)
                ProjectHTTPException.raise_http_500()
            except ClientResponseError as err:
                logger.error("ClientResponseError: status = {st}, {msg}", st=err.status, msg=err.message)
                ProjectHTTPException.raise_http_500()
            except ClientError as err:
                logger.error("ClientError: msg = {}", str(err))
                ProjectHTTPException.raise_http_500()

    except PaySystemNotAccountException:
        ProjectHTTPException.raise_http_404()
    except RepositoryError:
        ProjectHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("transaction_amount: {}", str(exp))
        ProjectHTTPException.raise_http_500()
    
    content = {
        "msg": f"Транзакция на сумму {amount}",
        "transaction_id": str(cash_payment.transaction_id),
        "server": message
    }    
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.post(
    "/transaction-webhook",
    response_model=CashAccountPayment,
    status_code=status.HTTP_201_CREATED,
    name="transaction",
)
async def transaction_webhook(
    payment: Annotated[CashPaymentSchema, Body()],
    db: Annotated["AsyncSession", Depends(get_async_db)]
):
    try:
        cps = CashPaymentRUBService(payment, db)        
        cash_payment: "CashPaymentBase" = await cps.process()

        cas = CashAccountRUBService(payment.user_id, db)
        cash_account: "CashAccountBase" = await cas.update_user_cash_account(payment.account_id, payment.amount)
        resp = CashAccountPayment(
            account=cash_account,
            payment=cash_payment
        )
    except PaySystemBalanceLessZeroException as exp:
        content = {"message": str(exp)}
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except PaySystemPaymentException as exp:
        ProjectHTTPException.raise_http_400(detail=str(exp))
    except PaySystemNotUserException:
        ProjectHTTPException.raise_http_404()
    except RepositoryError:
        ProjectHTTPException.raise_http_500()
    except Exception as exp:
        logger.error("transaction processing: {}", str(exp))
        ProjectHTTPException.raise_http_500()
    return resp
