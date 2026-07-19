from typing import TYPE_CHECKING
from uuid import UUID

from src.pay_system.exceptions import PaySystemNotAccountException
from src.pay_system.repository.cash_account_repo import CashAccountRepo
from src.pay_system.repository.cash_payment_repo import CashPaymentRepo
from src.pay_system.schemas.output.cash_payment_user import AccountCashPayments


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.schemas.output.user_base import UserBase
    from src.pay_system.schemas.output.cash_payment_base import CashPaymentBase
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase


class CashPaymentUserService:

    def __init__(self, user: "UserBase", db: "AsyncSession"):
        self.user = user
        self.db = db
    
    async def check_user_account(self, account_id: UUID) -> bool:
        """ Вернет True, если account существует и принадлежит пользователю, иначе False """
       
        account: "CashAccountBase | None" = await CashAccountRepo.select_account_by_id(account_id, self.db)
        result = account is not None and account.user_id == self.user.id
        return result
    
    async def get_user_account_payments(self, account_id: UUID, check_account: bool = True) -> AccountCashPayments:
        """ Получить перечень платежей по переданному account_id. Вернет объект AccountCashPayments. """

        if check_account:
            check: bool = await self.check_user_account(account_id)
            if not check:
                raise PaySystemNotAccountException(f"Передан некорректный счет: {account_id}")
        
        payments: list["CashPaymentBase"] = await CashPaymentRepo.select_payments_by_account(account_id, self.db)
        acp = AccountCashPayments(account_id=account_id, payments=payments)
        return acp
