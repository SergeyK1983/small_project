from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, computed_field


class UserDeleted(BaseModel):
    """ Удаленный пользователь """

    id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    username: Annotated[str, Field(description="Пользователь")]
    email: Annotated[EmailStr, Field(description="Почта")]
   