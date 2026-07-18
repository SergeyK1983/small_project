from typing import Annotated

from pydantic import BaseModel, Field

from .user_base import UserBase


class Users(BaseModel):
    users: Annotated[list[UserBase], Field(description="Список всех пользователей")]

