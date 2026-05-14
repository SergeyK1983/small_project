from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, computed_field


class UserBaseSchema(BaseModel):
    """ Схема для работы с пользователем """

    id: Annotated[UUID | None, Field(default=None, description="Идентификатор пользователя")]
    username: Annotated[str | None, Field(default=None, description="Пользователь")]
    email: Annotated[EmailStr | None, Field(default=None, description="Почта")]
    is_active: Annotated[bool | None, Field(default=None, description="Активированный пользователь")]
    is_staff: Annotated[bool | None, Field(default=None, description="Сотрудник")]
    is_superuser: Annotated[bool | None, Field(default=None, description="Администратор")]
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
