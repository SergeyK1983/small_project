from typing import Annotated

from pydantic import BaseModel, Field, EmailStr


class UserUpdateSchema(BaseModel):
    """ Изменение данных пользователя о себе """
    
    username: Annotated[str | None, Field(default=None, description="Пользователь")]
    email: Annotated[EmailStr | None, Field(default=None, description="Почта")]
    first_name: Annotated[str | None, Field(default=None, description="Имя")]
    second_name: Annotated[str | None, Field(default=None, description="Фамилия")]
    last_name: Annotated[str | None, Field(default=None, description="Отчество")]


class UserAdminUpdateSchema(BaseModel):
    """ Изменение данных пользователя администратором """
    
    is_active: Annotated[bool | None, Field(default=None, description="Активированный пользователь")]
    is_staff: Annotated[bool | None, Field(default=None, description="Сотрудник")]
    is_superuser: Annotated[bool | None, Field(default=None, description="Администратор")]

