from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, EmailStr

from src.auth.schemas.validators import validate_password, validate_username


ValidPassword = Annotated[str, AfterValidator(validate_password)]
ValidUsername = Annotated[str, AfterValidator(validate_username)]


class UserAuthSchema(BaseModel):
    """ Signup and Signin """
    
    username: Annotated[ValidUsername, Field(min_length=4, max_length=125, description="Имя пользователя в системе")]
    email: Annotated[EmailStr, Field(description="Электронная почта")]
    password: Annotated[ValidPassword, Field(description="Пароль")]


class UserSigninSchema(BaseModel):
    """ На случай если вход осуществляется с формы """
    
    username: Annotated[str, Field(description="Имя пользователя в системе")]
    email: Annotated[EmailStr, Field(description="Электронная почта")]
    password: Annotated[str, Field(description="Пароль")]


class OAuth2FormDataSchema(UserSigninSchema):
    """ На случай если вход осуществляется с формы """
    pass    
