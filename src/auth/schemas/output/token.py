from typing import Annotated

from pydantic import BaseModel, Field


class UserTokenSchema(BaseModel):
    """ Signin response """
    
    token: Annotated[str, Field(description="Токен пользователя")]
    token_type: Annotated[str, Field(description="Тип токена")]
