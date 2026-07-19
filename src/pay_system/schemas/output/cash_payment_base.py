from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from src.pay_system.constants import CoefficientMonetaryUnits


class CashPaymentBase(BaseModel):
    """ Схема для работы с платежной транзакцией """

    id: Annotated[UUID, Field(description="Идентификатор платежа")]
    created: Annotated[datetime, Field(description="Создан")]
    description: Annotated[str, Field(description="Описание")]
    amount: Annotated[int, Field(description="Сумма пополнения/списания, коп")]
    transaction_id: Annotated[UUID, Field(description="Идентификатор транзакции")]
    account_rub_id: Annotated[UUID, Field(description="Идентификатор счета")]

    @field_serializer("amount", mode="plain")
    def set_decimal(self, value: int) -> Decimal:
        d_value = Decimal(str(value / CoefficientMonetaryUnits.RUB)).quantize(Decimal("0.01"))
        return d_value

