from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, EmailStr, model_validator

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
    
    username: Annotated[str | None, Field(default=None, description="Имя пользователя в системе")]
    email: Annotated[EmailStr | None, Field(default=None, description="Электронная почта")]
    password: Annotated[str, Field(description="Пароль")]

    @model_validator(mode="after")
    def one_thing_required(self):
        if not(self.username or self.email):
            raise ValueError("username or email must be transmitted")
        return self

