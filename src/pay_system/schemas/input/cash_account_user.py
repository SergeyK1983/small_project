from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class CashAccountUser(BaseModel):
    """ Схема для работы с пользователем """

    user_id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    
