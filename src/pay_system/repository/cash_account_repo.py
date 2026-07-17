from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import RowMapping, Select, exists, select

from src.pay_system.models.cash_account import CashAccount
from src.pay_system.schemas.output.cash_account_base import CashAccountBase
from src.pay_system.schemas.output.cash_account_user import UserCashAccounts

from .cash_account_base_repo import CashAccountBaseRepo


class CashAccountRepo(CashAccountBaseRepo):
    
    @classmethod
    async def select_account_by_id(cls, account_id: UUID, db: AsyncSession) -> CashAccountBase | None:
        query = cls._select_cash_account_fields().where(CashAccount.id == account_id)

        result = await cls._select_execute_query(query, db)
        account_map: RowMapping | None = result.mappings().first()

        if not account_map:
            return None
        return CashAccountBase(**account_map)
    
    @classmethod
    async def is_exists_account_by_id(cls, account_id: UUID, db: AsyncSession) -> bool:
        query: Select = select(exists().where(CashAccount.id == account_id))
        
        result = await cls._select_execute_query(query, db)
        is_exists: bool = result.scalar() # type: ignore
        return is_exists
    
    @classmethod
    async def select_user_accounts(cls, user_id: UUID, db: AsyncSession) -> UserCashAccounts:
        query = cls._select_cash_account_fields().where(CashAccount.user_id == user_id)

        result = await cls._select_execute_query(query, db)
        rows: list[RowMapping] | list = result.mappings().fetchall() # type: ignore
        
        uca = UserCashAccounts(
            user_id=user_id,
            accounts=[
                CashAccountBase(
                    id=row["id"],
                    created=row["created"],
                    updated=row["updated"],
                    currency=row["currency"],
                    balance=row["balance"],
                    user_id=row["user_id"],
                ) for row in rows if row
            ]
        )
        return uca

