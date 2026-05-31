from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, computed_field


class UserBase(BaseModel):
    """ Схема для работы с пользователем """

    id: Annotated[UUID, Field(description="Идентификатор пользователя")]
    username: Annotated[str, Field(description="Пользователь")]
    email: Annotated[EmailStr, Field(description="Почта")]
    is_active: Annotated[bool, Field(description="Активированный пользователь")]
    is_staff: Annotated[bool, Field(description="Сотрудник")]
    is_superuser: Annotated[bool, Field(description="Администратор")]
    first_name: Annotated[str | None, Field(default=None, description="Имя")]
    second_name: Annotated[str | None, Field(default=None, description="Фамилия")]
    last_name: Annotated[str | None, Field(default=None, description="Отчество")]

    @computed_field
    @property
    def full_name(self) -> str:
        """ ФИО """
        
        f_name = " ".join(
            filter(None, [
                self.second_name,
                self.first_name,
                self.last_name
            ])
        )
        return f_name
