from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserDeleted(BaseModel):
    """ Удаленный пользователь """

    id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    username: Annotated[str, Field(description="Пользователь")]
    email: Annotated[EmailStr, Field(description="Почта")]


class UserLightDeleted(BaseModel):
    """ Слегка Удаленный пользователь """

    id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    username: Annotated[str, Field(description="Пользователь")]
    email: Annotated[EmailStr, Field(description="Почта")]
    is_active: Annotated[bool, Field(description="Активированный пользователь")]
