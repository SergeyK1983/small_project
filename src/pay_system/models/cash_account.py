from datetime import datetime
from uuid import uuid4
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, func, UUID, BIGINT, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.auth.models.user import User
    from src.pay_system.models.cash_payment import CashPayment


class CashAccount(Base):
    """ Платежный счет в рублях """
    
    __tablename__ = "cash_accounts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="Дата создания"
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Дата изменения"
    )
    currency: Mapped[str] = mapped_column(
        String(length=3), default="RUB", nullable=False, comment="Денежная единица"
    )
    balance: Mapped[int] = mapped_column(
        BIGINT, nullable=False, default=0, comment="Баланс в копейках"
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id",  ondelete='CASCADE'))
    user: Mapped["User"] = relationship(back_populates="accounts_rub", single_parent=True)

    payments: Mapped[list["CashPayment"]] = relationship(
         back_populates="cash_account", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("cash_accounts_user_id_idx", user_id),
    )

    def __repr__(self):
        return f"{self.id}-{self.currency}"

