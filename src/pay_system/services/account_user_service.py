from typing import TYPE_CHECKING

from src.pay_system.repository.cash_account_repo import CashAccountRepo


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.schemas.output.user_base import UserBase
    from src.pay_system.schemas.output.cash_account_user import UserCashAccounts


class CashAccountUserService:

    def __init__(self, user: "UserBase", db: "AsyncSession"):
        self.user = user
        self.db = db
    
    async def get_user_accounts(self) -> "UserCashAccounts":
        accounts: "UserCashAccounts" = await CashAccountRepo.select_user_accounts(self.user.id, self.db)

        return accounts
