from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, EmailStr

from src.auth.schemas.validators import validate_password, validate_username


ValidPassword = Annotated[str, AfterValidator(validate_password)]
ValidUsername = Annotated[str, AfterValidator(validate_username)]


class UserSignupSchema(BaseModel):
    """ Signup (Регистрация) """
    
    username: Annotated[ValidUsername, Field(min_length=4, max_length=125, description="Имя пользователя в системе")]
    email: Annotated[EmailStr, Field(description="Электронная почта")]
    password: Annotated[ValidPassword, Field(description="Пароль")]


class UserAuthSchema(BaseModel):
    """ Signin (Вход) """
    
    username: Annotated[str, Field(description="Имя пользователя в системе")]
    email: Annotated[EmailStr, Field(description="Электронная почта")]
    password: Annotated[str, Field(description="Пароль")]

