from typing import TYPE_CHECKING

from src.pay_system.repository.cash_account_repo import CashAccountRepo
from src.pay_system.schemas.output.cash_account_user import UserCashAccounts


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.auth.schemas.output.user_base import UserBase
    from src.pay_system.schemas.output.cash_account_base import CashAccountBase


class CashAccountUserService:

    def __init__(self, user: "UserBase", db: "AsyncSession"):
        self.user = user
        self.db = db
    
    async def get_user_accounts(self) -> UserCashAccounts:
        accounts: list["CashAccountBase"] = await CashAccountRepo.select_user_accounts(self.user.id, self.db)

        uca = UserCashAccounts(user_id=self.user.id, accounts=accounts)
        return uca
