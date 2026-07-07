from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, EmailStr

from src.auth.schemas.validators import validate_password


ValidPassword = Annotated[str, AfterValidator(validate_password)]


class UserChangePasswordSchema(BaseModel):
    """ Смена пароля пользователем """
    
    email: Annotated[EmailStr, Field(description="Электронная почта")]
    password_old: Annotated[str, Field(description="Пароль старый")]
    password_new: Annotated[ValidPassword, Field(description="Пароль новый")]
    password_rep: Annotated[str, Field(description="Пароль повтор")]

