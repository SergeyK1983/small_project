from sqlalchemy import RowMapping, insert, select, Select, Result
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RepositoryDatabaseError, RepositoryError, RepositoryIntegrityError
from src.core.logger import logger
from src.pay_system.models.cash_payment import CashPayment
from src.pay_system.schemas.output.cash_payment_base import CashPaymentBase


class CashPaymentBaseRepo:

    @staticmethod
    def _select_cash_payment_fields() -> Select:
        """Основные данные пользователя"""

        query = select(
            CashPayment.id,
            CashPayment.created,
            CashPayment.description,
            CashPayment.amount,
            CashPayment.transaction_id,
            CashPayment.account_rub_id
        )
        return query

    @staticmethod
    async def _select_execute_query(query: Select, db: AsyncSession) -> Result:
        """Select запрос в БД"""
        try:
            result: Result = await db.execute(query)
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        return result
    
    @classmethod
    async def insert_cash_payment(cls, values: dict, db: AsyncSession) -> CashPaymentBase:

        query = (
            insert(
                CashPayment
            ).
            values(
                amount=values["amount"],
                transaction_id=values["transaction_id"],
                account_rub_id=values["account_rub_id"],
                description=(
                    values["description"] if values.get("description") and values["description"] is not None else ""
                )
            ).
            returning(
                CashPayment
            )
        )
        try:
            result = await db.execute(query)            
            created: RowMapping | None = result.mappings().fetchone()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp

        if created is None:
            await db.rollback()
            raise RepositoryError("CashPayment create error, created must not be None")
        
        await db.commit()
        return CashPaymentBase.model_validate(created["CashPayment"], from_attributes=True)
    