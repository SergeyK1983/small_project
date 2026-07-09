from typing import TYPE_CHECKING
from uuid import UUID

from src.auth.repository.user_registered_repository import UserRegisteredRepo
from src.pay_system.exceptions import PaySystemNotUserException
from src.pay_system.repository.cash_account_create_repo import CashAccountCreateRepo


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession    
    from src.auth.schemas.output.user_base import UserBase
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase


class CashAccountBaseService:

    user_id: UUID
    db_session: "AsyncSession"

    async def create_user_cash_account(self) -> "CashAccountBase":
        """ Создает пользователю платежный счет """

        user: "UserBase | None" = await UserRegisteredRepo.read_one_user_by_id(self.user_id, self.db_session)

        if not user:
            raise PaySystemNotUserException

        account: "CashAccountBase" = await CashAccountCreateRepo.create_cash_account(self.user_id, self.db_session)
        return account
    
    async def update_user_cash_account(self):
        """ Обновляет баланс платежного счета """
        pass


class CashAccountService(CashAccountBaseService):

    def __init__(self, user_id: UUID, db: "AsyncSession"):
        self.user_id: UUID = user_id
        self.db_session: "AsyncSession" = db

