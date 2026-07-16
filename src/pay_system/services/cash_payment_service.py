import hashlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.core.config import settings
from src.pay_system.constants import CoefficientMonetaryUnits
from src.pay_system.exceptions import PaySystemPaymentException
from src.pay_system.repository.cash_account_repo import CashAccountRepo
from src.pay_system.repository.cash_payment_repo import CashPaymentRepo


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.pay_system.schemas.input.cash_payment_webhook import CashPaymentSchema
    from src.pay_system.schemas.output.cash_payment_base import CashPaymentBase


class CashPaymentBaseService(ABC):
    """ Работа с платежами """
    
    payment: "CashPaymentSchema"
    db: "AsyncSession"

    def _verify_signature(self) -> bool:
        """ 
        Проверка подписи. Правило: {account_id}{amount}{transaction_id}{user_id}{secret_key}
        Вернет True, если подпись корректна, иначе False
        """

        hash_ = hashlib.sha256()
        hash_.update(f"{self.payment.account_id}".encode(encoding="utf-8"))
        hash_.update(f"{self.payment.amount}".encode(encoding="utf-8"))
        hash_.update(f"{self.payment.transaction_id}".encode(encoding="utf-8"))
        hash_.update(f"{self.payment.user_id}".encode(encoding="utf-8"))
        hash_.update(f"{settings.payment_key}".encode(encoding="utf-8"))
        
        signature_hash: str = hash_.hexdigest()
        verify: bool = signature_hash == self.payment.signature
        return verify

    async def _check_user_exists(self) -> bool:
        """ Проверка пользователя """
        
        exists: bool = await UserRegisteredRepo.is_exists_and_active_user_by_id(self.payment.user_id, self.db)
        return exists

    async def _check_cash_account_exists(self) -> bool:
        """ Проверка наличия счета """
        exists: bool = await CashAccountRepo.is_exists_account_by_id(self.payment.account_id, self.db)
        return exists

    async def _check_transaction_uniq(self) -> bool:
        """ Проверка транзакции на уникальность. Вернет True, если transaction_id будет уникальной. """
        exists: bool = await CashPaymentRepo.is_exists_transaction(self.payment.transaction_id, self.db)
        return not exists
    
    async def process(self) -> "CashPaymentBase":
        """ Выполнит необходимые проверки и сохранит платеж в БД. """

        is_verify = self._verify_signature()
        if not is_verify:
            PaySystemPaymentException("Транзакция не прошла проверку подписи")
        
        is_user = await self._check_user_exists()
        if not is_user:
            PaySystemPaymentException("Не найден пользователь для проведения операции")
        
        is_account = await self._check_cash_account_exists()
        if not is_account:
            PaySystemPaymentException("Не найден счет для проведения операции")
        
        is_uniq = await self._check_transaction_uniq()
        if not is_uniq:
            PaySystemPaymentException("Операция не может быть проведена повторно")
        
        payment: "CashPaymentBase" = await self.save_payment()
        return payment
    
    @abstractmethod
    def convert_monetary_units(self) -> int:
        pass
    
    @abstractmethod
    async def save_payment(self) -> "CashPaymentBase":
        pass


class CashPaymentRUBService(CashPaymentBaseService):
    """ Работа с рублевыми платежами """

    def __init__(self, payment: "CashPaymentSchema", db: "AsyncSession"):
        self.payment = payment
        self.db = db

    def convert_monetary_units(self) -> int:
        return int(self.payment.amount * CoefficientMonetaryUnits.RUB)
    
    async def save_payment(self) -> "CashPaymentBase":
        """ Сохранение платежа """
        
        values = {
            "amount": self.convert_monetary_units(),
            "account_rub_id": self.payment.account_id,
            "transaction_id": self.payment.transaction_id,
            "description": self.payment.description,
        }

        payment: "CashPaymentBase" = await CashPaymentRepo.insert_cash_payment(values, self.db)
        return payment
