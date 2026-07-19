from decimal import Decimal

from sqladmin import ModelView

from src.pay_system.constants import CoefficientMonetaryUnits
from src.pay_system.models.cash_account import CashAccount


class CashAccountAdmin(ModelView, model=CashAccount):
    column_list = [
        CashAccount.id, 
        CashAccount.created, 
        CashAccount.updated, 
        CashAccount.currency, 
        CashAccount.balance,
        CashAccount.user,
    ]
    column_searchable_list = [CashAccount.user]
    column_sortable_list = [CashAccount.created]
    can_create = False
    can_edit = False
    can_delete = False
    name = "Платежный счет"
    name_plural = "Платежные счета"
    category = "pay_system"

    column_formatters = {
        CashAccount.balance: lambda m, a: Decimal(
            str(m.balance / CoefficientMonetaryUnits.RUB)).quantize(Decimal("0.01")
        )
    }
    column_formatters_detail = {
        CashAccount.balance: lambda m, a: Decimal(
            str(m.balance / CoefficientMonetaryUnits.RUB)).quantize(Decimal("0.01")
        )
    }
