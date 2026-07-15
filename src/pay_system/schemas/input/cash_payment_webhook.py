import hashlib
from decimal import Decimal, InvalidOperation
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field, field_serializer, field_validator

from src.core.config import settings


class Amount(BaseModel):
    """ Роут обработки """

    amount: Annotated[
        Decimal, 
        Field(max_digits=15, decimal_places=2, description="сумма пополнения/списания", examples=[100.25, -3200])
    ]
    account_id: Annotated[UUID, Field(description="Идентификатор платежного счета")]

    @field_validator("amount", mode="before")
    @classmethod
    def check_amount(cls, value: str) -> Decimal:
        if value == 0 or value == "" or value is None:
            raise ValueError(f"Транзакция на сумму {value} не обрабатывается")
        try:
            value_d = Decimal(value)
        except InvalidOperation:
            raise ValueError(f"Транзакция на сумму {value} не обрабатывается")

        return value_d
    
    @field_validator("account_id", mode="before")
    @classmethod
    def check_account_id(cls, value: str) -> UUID:
        if value == "" or value is None:
            raise ValueError(f"Транзакция на счет {value} не обрабатывается")
        try:
            value_u = UUID(value)
        except ValueError:
            raise ValueError(f"Транзакция на счет {value} не обрабатывается")

        return value_u


class CashPaymentWebhook(BaseModel):
    """ Вебхук от сторонней платёжной системы """

    transaction_id: Annotated[
        UUID | None, 
        Field(default_factory=lambda: uuid4(), description="Идентификатор транзакции")
    ]
    user_id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    account_id: Annotated[UUID, Field(description="Идентификатор платежного счета")]
    amount: Annotated[
        Decimal, 
        Field(max_digits=15, decimal_places=2, description="сумма пополнения/списания", examples=[100.25, -3200])
    ]

    @field_serializer("transaction_id", "user_id", "account_id", "amount", mode="plain")
    def set_str(self, value: UUID) -> str:
        return str(value)
    
    @computed_field
    @property
    def signature(self) -> str:
        """
        Подпись платежа.
        Правило: {account_id}{amount}{transaction_id}{user_id}{secret_key} 
        """
        signature: bytes = f"{self.account_id}{self.amount}{self.transaction_id}{self.user_id}{settings.payment_key}"\
            .encode(encoding="utf-8")
        
        signature_hash: str = hashlib.sha256(data=signature).hexdigest()
        return signature_hash


class CashPaymentSchema(BaseModel):
    """ Входные данные от сторонней платёжной системы """

    transaction_id: Annotated[UUID, Field(description="Идентификатор транзакции")]
    user_id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    account_id: Annotated[UUID, Field(description="Идентификатор платежного счета")]
    amount: Annotated[
        Decimal, 
        Field(max_digits=15, decimal_places=2, description="сумма пополнения/списания", examples=[100.25, -3200])
    ]
    signature: Annotated[str, Field(description="Подпись с секретным ключом")]
    
