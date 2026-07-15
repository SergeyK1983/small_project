from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import RowMapping, select

from src.pay_system.models.cash_account import CashAccount
from src.pay_system.schemas.output.cash_account_base import CashAccountBase

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

