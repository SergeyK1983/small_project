from sqlalchemy import select, Select, Result
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RepositoryDatabaseError, RepositoryIntegrityError
from src.core.logger import logger
from src.pay_system.models.cash_account import CashAccount


class CashAccountBaseRepo:

    @staticmethod
    def _select_cash_account_fields() -> Select:
        """Основные данные пользователя"""

        query = select(
            CashAccount.id,
            CashAccount.created,
            CashAccount.updated,
            CashAccount.balance,
            CashAccount.currency,
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
    