from typing import TYPE_CHECKING
from uuid import UUID

from src.pay_system.repository.cash_account_repo import CashAccountRepo
from src.pay_system.schemas.output.cash_account_user import UserCashAccounts


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase


class CashAccountAdminService:

    def __init__(self, user_id: UUID, db: "AsyncSession"):
        self.user_id = user_id
        self.db = db
    
    async def get_user_accounts(self) -> UserCashAccounts:
        accounts: list["CashAccountBase"] = await CashAccountRepo.select_user_accounts(self.user_id, self.db)

        uca = UserCashAccounts(user_id=self.user_id, accounts=accounts)
        return uca
