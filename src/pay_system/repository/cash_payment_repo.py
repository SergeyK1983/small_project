from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import RowMapping, Select, exists, select

from src.pay_system.models.cash_payment import CashPayment
from src.pay_system.schemas.output.cash_payment_base import AccountCashPayments, CashPaymentBase

from .cash_payment_base_repo import CashPaymentBaseRepo


class CashPaymentRepo(CashPaymentBaseRepo):
    
    @classmethod
    async def select_payment_by_id(cls, payment_id: UUID, db: AsyncSession) -> CashPaymentBase | None:
        query = cls._select_cash_payment_fields().where(CashPayment.id == payment_id)

        result = await cls._select_execute_query(query, db)
        account_map: RowMapping | None = result.mappings().first()

        if not account_map:
            return None
        return CashPaymentBase(**account_map)
    
    @classmethod
    async def select_payments_by_account(cls, account_id: UUID, db: AsyncSession) -> AccountCashPayments | None:
        query = cls._select_cash_payment_fields().where(CashPayment.account_rub_id == account_id)

        result = await cls._select_execute_query(query, db)
        rows: list[RowMapping] = result.mappings().fetchall()  # type: ignore # pet-проект, грузим всё в память

        if not rows:
            return None
        
        acp = AccountCashPayments(
            account_id=account_id,
            payments=[CashPaymentBase(
                id=row["id"],
                created=row["created"],
                description=row["description"],
                amount=row["amount"],
                transaction_id=row["transaction_id"],
                account_rub_id=row["account_rub_id"]
            ) for row in rows if row]
        )
        return acp
    
    @classmethod
    async def is_exists_transaction(cls, transaction_id: UUID, db: AsyncSession) -> bool:
        query: Select = select(exists().where(CashPayment.transaction_id == transaction_id))
        
        result = await cls._select_execute_query(query, db)
        is_exists: bool = result.scalar() # type: ignore
        return is_exists

