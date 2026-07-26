from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class UserChangePWD(BaseModel):
    """ Пользователь сменил пароль """

    id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    username: Annotated[str, Field(description="Пользователь")]

    @field_serializer("id", mode="plain")
    def set_str(self, value: UUID) -> str:
        return str(value)
