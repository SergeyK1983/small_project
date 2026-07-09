from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class CashAccountBase(BaseModel):
    """ Схема для работы с платежным счетом """

    id: Annotated[UUID, Field(description="Идентификатор счета")]
    created: Annotated[datetime, Field(description="Создан")]
    updated: Annotated[datetime, Field(description="Обновлен")]
    currency: Annotated[str, Field(description="Валюта")]
    balance: Annotated[int, Field(description="Баланс на счете")]
    user_id: Annotated[UUID, Field(description="Пользователь счета")]
    
    
