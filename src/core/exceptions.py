from typing import NoReturn

from fastapi import HTTPException, status


class RepositoryError(Exception):
    """Базовая ошибка репозитория."""
    pass


class RepositoryIntegrityError(RepositoryError):
    """Нарушение целостности данных."""
    pass


class RepositoryDatabaseError(RepositoryError):
    """Общая ошибка БД."""
    pass


class ProjectBaseException(Exception):
    pass


class ProjectHTTPException(ProjectBaseException):

    @classmethod
    def raise_http_500(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Server error"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    @classmethod
    def raise_http_404(cls, detail: str | None = None) -> NoReturn:
        if detail is None:
            detail = "Not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
