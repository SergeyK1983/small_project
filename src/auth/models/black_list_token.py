from datetime import date

from sqlalchemy import Date, func, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class BlackToken(Base):
    """ Черный список токенов """
    
    __tablename__ = "black_tokens"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    created: Mapped[date] = mapped_column(
        Date, server_default=func.current_date(), comment="День создания"
    )    
    jti: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True, comment="Токен uuid"
    )

    def __repr__(self):
        return f"{self.id}-{self.jti}"