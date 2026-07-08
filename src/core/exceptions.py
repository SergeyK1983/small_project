class RepositoryError(Exception):
    """Базовая ошибка репозитория."""
    pass


class RepositoryIntegrityError(RepositoryError):
    """Нарушение целостности данных."""
    pass


class RepositoryDatabaseError(RepositoryError):
    """Общая ошибка БД."""
    pass
