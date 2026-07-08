from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import String, Boolean, DateTime, func, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.pay_system.models.cash_account import CashAccount


class User(Base):
    """ Пользователь """
    
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="Дата создания"
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Дата изменения"
    )
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True, comment="Пользователь"
    )
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True, comment="Почта"
    )
    password: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Суперпользователь"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Активен"
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Персонал"
    )
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Имя"
    )
    second_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Фамилия"
    )
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Отчество"
    )

    accounts_rub: Mapped[list["CashAccount"]] = relationship(
         back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("username", name="user_username_key_uniq"),
        UniqueConstraint("email", name="user_email_key_uniq"),
    )

    def __repr__(self):
        return f"{self.id}-{self.username}"

