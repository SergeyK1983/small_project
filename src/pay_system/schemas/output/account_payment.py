from typing import Annotated

from pydantic import BaseModel, Field

from .cash_account_base import CashAccountBase
from .cash_payment_base import CashPaymentBase


class CashAccountPayment(BaseModel):
    """ Контроль состояния счета после пополнения/списания """

    account: Annotated[CashAccountBase, Field(description="Платежный счет")]
    payment: Annotated[CashPaymentBase, Field(description="Совершенная транзакция")]
