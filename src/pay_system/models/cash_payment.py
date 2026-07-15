from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import BigInteger, ForeignKey, Index, String, DateTime, func, UUID, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.pay_system.models.cash_account import CashAccount


class CashPayment(Base):
    """ Платеж. Денежный перевод. """

    __tablename__ = "cash_payments"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="Дата создания"
    )
    description: Mapped[str] = mapped_column(
        String, default=text(""), comment="Описание операции"
    )
    amount: Mapped[int] = mapped_column(
        BigInteger, comment="Сумма пополнения/списания в коп."
    )
    transaction_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), comment="код транзакции"
    )

    account_rub_id: Mapped[UUID] = mapped_column(ForeignKey("cash_accounts.id",  ondelete='CASCADE'))
    cash_account: Mapped["CashAccount"] = relationship(back_populates="payments", single_parent=True)

    __table_args__ = (
        Index("cash_payments_account_rub_id_idx", account_rub_id),
        UniqueConstraint(transaction_id, name="cash_payments_transaction_id_uniq")
    )

    def __repr__(self):
        return f"{self.id}-{self.amount}"
