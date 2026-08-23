from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from src.pay_system.exceptions import PaySystemNotAccountException
from src.pay_system.repository.cash_account_repo import CashAccountRepo
from src.pay_system.schemas.input.cash_payment_webhook import CashPaymentWebhook

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase


class ThirdPaymentSystem:
    """ Сторонняя платежная система """

    def __init__(self, db: "AsyncSession"):
        self.db: "AsyncSession" = db
    
    async def check_account_id(self, account_id: UUID) -> "CashAccountBase":
        """ 
        Проверяет существует счет с account_id. 
        Вернет объект CashAccountBase или поднимет исключение ThirdPaymentSystemNotAccount.
        """
        cash_account: "CashAccountBase | None" = await CashAccountRepo.select_account_by_id(account_id, self.db)
        
        if not cash_account:
            raise PaySystemNotAccountException("There is no billing account")

        return cash_account
    
    def prepare_data_webhook(self, amount: Decimal, account_id: UUID, user_id: UUID) -> CashPaymentWebhook:
        
        if not isinstance(amount, Decimal):
            raise ValueError(f"The payment must be an Decimal number, not a {amount = }")

        cpw = CashPaymentWebhook(account_id=account_id, user_id=user_id, amount=amount) # type: ignore
        return cpw

