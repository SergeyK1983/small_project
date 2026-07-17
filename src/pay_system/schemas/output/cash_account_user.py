from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from .cash_account_base import CashAccountBase


class UserCashAccounts(BaseModel):
    """ Все счета пользователя """
    
    user_id: Annotated[UUID, Field(description="Пользователь счета")]
    accounts: Annotated[list[CashAccountBase], Field(description="Счета пользователя")]

