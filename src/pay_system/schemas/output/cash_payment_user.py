from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from .cash_payment_base import CashPaymentBase


class AccountCashPayments(BaseModel):
    """ Перечень платежей для счета """
    
    account_id: Annotated[UUID, Field(description="Идентификатор счета")]
    payments: Annotated[list[CashPaymentBase], Field(description="Платежи")]

