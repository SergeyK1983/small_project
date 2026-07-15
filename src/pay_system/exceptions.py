class PaySystemBaseException(Exception):
    pass


class PaySystemNotUserException(PaySystemBaseException):
    """ Не найден пользователь, для которого выполняется операция """
    pass


class PaySystemNotAccountException(PaySystemBaseException):
    pass
