class PaySystemBaseException(Exception):
    pass


class PaySystemNotUserException(PaySystemBaseException):
    """ Не найден пользователь, для которого выполняется операция """
    pass


class PaySystemNotAccountException(PaySystemBaseException):
    """ Не найден счет, для которого выполняется операция """
    pass


class PaySystemPaymentException(PaySystemBaseException):
    """ Ошибка при выполнении/обработке платежа """
    pass


class PaySystemBalanceLessZeroException(PaySystemBaseException):
    """ Баланс на счете будет меньше нуля после операции """
    pass

