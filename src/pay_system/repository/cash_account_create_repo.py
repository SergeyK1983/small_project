from uuid import UUID

from sqlalchemy import Insert, Result, Update, RowMapping, desc, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RepositoryDatabaseError, RepositoryError, RepositoryIntegrityError
from src.pay_system.models.cash_account import CashAccount
from src.pay_system.repository.cash_account_base_repo import CashAccountBaseRepo
from src.pay_system.schemas.output.cash_account_base import CashAccountBase
from src.core.logger import logger


class CashAccountCreateUpdateRepo(CashAccountBaseRepo):
    """ Первичное создание платежного счета для пользователя с нулевым балансом """

    @classmethod
    async def __create(cls, user_id: UUID, query: Insert, db: AsyncSession) -> CashAccountBase:
        try:
            await db.execute(query)
            await db.commit()

            result = await db.execute(
                cls._select_cash_account_fields()
                .where(
                    CashAccount.user_id == user_id
                )
                .order_by(
                    desc(CashAccount.created)
                )
            )
            created: RowMapping | None = result.mappings().first()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp

        if created is None:
            raise RepositoryError("CashAccount create error, created must not be None")

        logger.success(
            "Счет id={account_id} для пользователя {user_id} создан!", account_id=created["id"], user_id=user_id
        )
        return CashAccountBase(**created)
    
    @classmethod
    async def __update(cls, query: Update, db: AsyncSession) -> Result:
        try:
            result = await db.execute(query)            
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        
        return result
    
    @classmethod
    async def create_cash_account(cls, user_id: UUID, db: AsyncSession) -> CashAccountBase:
        """
        Запрос на создание платежного счета для пользователя
        Args:
            user_id: user_id of user
        Returns:
            created CashAccountBase
        """
        query = insert(CashAccount).values(
            user_id=user_id,
            
        )
        result: CashAccountBase = await cls.__create(user_id, query, db)
        return result
    
    @classmethod
    async def update_cash_account(cls, account_id: UUID, amount: int, db: AsyncSession) -> CashAccountBase:
        """ 
        Запрос для обновления баланса платежного счета
        Args:
            account_id: номер счета
            amount: сумма пополнения/списания
        Returns:
            updated obj CashAccountBase
        """
        query = (
            update(
                CashAccount
            ).
            where(
                CashAccount.id == account_id
            ).
            values(
                balance=CashAccount.balance + amount
            ).
            returning(
                CashAccount
            )
        )        
        result = await cls.__update(query, db)
        updated: RowMapping | None = result.mappings().fetchone()
        
        if updated is None:
            await db.rollback()
            raise RepositoryError("CashAccount update error, updated must not be None")
        
        await db.commit()

        return CashAccountBase.model_validate(updated["CashAccount"], from_attributes=True)
