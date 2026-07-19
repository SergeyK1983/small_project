from decimal import Decimal

from sqladmin import ModelView

from src.pay_system.constants import CoefficientMonetaryUnits
from src.pay_system.models.cash_payment import CashPayment


class CashPaymentAdmin(ModelView, model=CashPayment):
    column_list = [
        CashPayment.id, 
        CashPayment.created, 
        CashPayment.description, 
        CashPayment.amount,
        CashPayment.transaction_id,
        CashPayment.account_rub_id,
    ]
    column_searchable_list = [CashPayment.id]
    column_sortable_list = [CashPayment.created]
    can_create = False
    can_edit = False
    can_delete = False
    name = "Пополнение/Списание"
    name_plural = "Платежи"
    category = "pay_system"

    column_formatters = {
        CashPayment.amount: lambda m, a: Decimal(
            str(m.amount / CoefficientMonetaryUnits.RUB)).quantize(Decimal("0.01")
        )
    }
    column_formatters_detail = {
        CashPayment.amount: lambda m, a: Decimal(
            str(m.amount / CoefficientMonetaryUnits.RUB)).quantize(Decimal("0.01")
        )
    }
