from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from src.pay_system.constants import CoefficientMonetaryUnits


class CashAccountBase(BaseModel):
    """ Схема для работы с платежным счетом """

    id: Annotated[UUID, Field(description="Идентификатор счета")]
    created: Annotated[datetime, Field(description="Создан")]
    updated: Annotated[datetime, Field(description="Обновлен")]
    currency: Annotated[str, Field(description="Валюта")]
    balance: Annotated[int, Field(description="Баланс на счете")]
    user_id: Annotated[UUID, Field(description="Пользователь счета")]

    @field_serializer("balance", mode="plain")
    def set_decimal(self, value: int) -> Decimal:
        d_value = Decimal(str(value / CoefficientMonetaryUnits.RUB)).quantize(Decimal("0.01"))
        return d_value
    
    
