from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.pay_system.constants import CoefficientMonetaryUnits
from src.pay_system.exceptions import PaySystemNotAccountException, PaySystemNotUserException
from src.pay_system.repository.cash_account_create_repo import CashAccountCreateUpdateRepo
from src.pay_system.repository.cash_account_repo import CashAccountRepo


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession    
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase


class CashAccountBaseService(ABC):

    user_id: UUID
    db_session: "AsyncSession"

    async def _check_user_exists(self) -> bool:
        """ True если пользователь существует и активен, иначе Else """
        
        exists: bool = await UserRegisteredRepo.is_exists_and_active_user_by_id(self.user_id, self.db_session)
        return exists
    
    async def _check_account_exists(self, account_id: UUID) -> bool:
        """ True если счёт существует, иначе Else """
        
        exists: bool = await CashAccountRepo.is_exists_account_by_id(account_id, self.db_session)
        return exists
    
    @abstractmethod
    def convert_monetary_units(self, amount: Decimal) -> int:
        pass
    
    @abstractmethod
    async def create_user_cash_account(self) -> "CashAccountBase":
        """ Создает пользователю платежный счет """
        pass
    
    @abstractmethod
    async def update_user_cash_account(self, account_id: UUID, amount: Decimal) -> "CashAccountBase":
        """ Обновляет баланс платежного счета на переданную сумму """
        pass        


class CashAccountRUBService(CashAccountBaseService):

    def __init__(self, user_id: UUID, db: "AsyncSession"):
        self.user_id: UUID = user_id
        self.db_session: "AsyncSession" = db
    
    def convert_monetary_units(self, amount: Decimal) -> int:
        return int(amount * CoefficientMonetaryUnits.RUB)

    async def create_user_cash_account(self) -> "CashAccountBase":
        """ Создает пользователю платежный счет """

        exists = await self._check_user_exists()
        if not exists:
            raise PaySystemNotUserException

        account: "CashAccountBase" = await CashAccountCreateUpdateRepo.create_cash_account(
            self.user_id, self.db_session
        )
        return account
    
    async def update_user_cash_account(self, account_id: UUID, amount: Decimal) -> "CashAccountBase":
        """ Обновляет баланс платежного счета на переданную сумму """
        
        exists = await self._check_user_exists()
        if not exists:
            raise PaySystemNotUserException
        
        account_check: "CashAccountBase | None" = await CashAccountRepo.select_account_by_id(
            account_id, self.db_session
        )
        
        if not account_check or account_check.user_id != self.user_id or account_check.currency != "RUB":
            raise PaySystemNotAccountException        
        
        amount_unit: int = self.convert_monetary_units(amount)        
        account: "CashAccountBase" = await CashAccountCreateUpdateRepo.update_cash_account(
            account_id, amount_unit, self.db_session
        )
        return account

