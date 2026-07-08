from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import RowMapping, delete, insert, select, Select, exists
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RepositoryDatabaseError, RepositoryError, RepositoryIntegrityError
from src.auth.models.black_list_token import BlackToken
from src.core.logger import logger


class TokenRepo:

    @staticmethod
    def _select_token_fields() -> Select:
        """Основные данные пользователя"""

        query = select(
            BlackToken.created,
            BlackToken.jti
        )
        return query

    @classmethod
    async def is_exists_black_token(cls, jti: UUID, db: AsyncSession) -> bool:
        query: Select = select(exists().where(BlackToken.jti == jti))
        try:
            result: bool = await db.scalar(query)  # type: ignore
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        return result
    
    @classmethod
    async def insert_token(cls, jti: UUID, db: AsyncSession) -> None:
        """
        Запрос на запись токена в черный список
        Args:
            jti: token ID
            db: AsyncSession
        Returns:
            None
        """
        query = insert(BlackToken).values(jti=jti)

        try:
            await db.execute(query)
            await db.commit()

            result = await db.execute(
                cls._select_token_fields().where(BlackToken.jti == jti)
            )
            token: RowMapping | None = result.mappings().first()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp

        if token is None:
            raise RepositoryError("Token black list insert error, jti must not be None")        
        return
    
    @classmethod
    async def clear_tokens(cls, db: AsyncSession) -> None:
        """ Удаляет все записи старше 2-х дней от текущего времени """

        hours_24_ago: datetime = datetime.now() - timedelta(days=2)

        query = (
            delete(BlackToken)
            .where(
                BlackToken.created <= hours_24_ago.date(),
            )
        )
        try:
            await db.execute(query)
            await db.commit()
        except IntegrityError as exp:
            logger.exception("Integrity error in query", extra={"query": str(query)})
            raise RepositoryIntegrityError("Integrity constraint violated") from exp
        except DatabaseError as exp:
            logger.exception("Database error in query", extra={"query": str(query)})
            raise RepositoryDatabaseError("Database operation failed") from exp
        
        return None
