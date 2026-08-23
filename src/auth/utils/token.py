from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from uuid import UUID, uuid4

import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.security import APIKeyHeader, APIKeyCookie

from src.auth.exceptions import AuthHTTPException
from src.core.config import settings
from src.core.logger import logger


class TypeHeaderToken(Enum):
    ACCESS = APIKeyHeader(name="Authorization", auto_error=False)
    ACCESS_MIDDLEWARE = "Authorization"

    @classmethod
    def all_names(cls) -> list:
        return cls._member_names_


class TypeCookieToken(Enum):
    ACCESS = APIKeyCookie(name="access_token", auto_error=False)
    ACCESS_MIDDLEWARE = "access_token"

    @classmethod
    def all_names(cls) -> list:
        return cls._member_names_


@dataclass
class Payload:
    uid: UUID
    sub: str
    iss: str
    exp: datetime
    jti: UUID
    iat: datetime
    nbf: datetime
    type: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


class Token:

    @staticmethod
    def __get_payload(user_id: UUID, token_type: str) -> Payload:
        current_time = datetime.now(timezone.utc)

        if token_type == TypeHeaderToken.ACCESS.name:
            time_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            raise TypeError(f"Token type {token_type} not supported")

        payload = Payload(
            uid=jsonable_encoder(user_id),
            sub=str(user_id),
            iss=settings.APPLICATION,
            exp=current_time + time_delta,
            jti=jsonable_encoder(uuid4()),
            iat=current_time,
            nbf=current_time,
            type=token_type,
        )
        return payload

    def _create_token(self, user_id: UUID, token_type) -> str:
        payload: Payload = self.__get_payload(user_id, token_type)
        try:
            encoded = jwt.encode(payload=payload.as_dict(), key=settings.private_key, algorithm=settings.ALGORITHM) # type: ignore
        except jwt.InvalidKeyError:
            AuthHTTPException.raise_http_500()
        return encoded

    @staticmethod
    def _decode_token(encoded: str) -> Payload:
        if not encoded.startswith("JWT "):
             AuthHTTPException.raise_http_401()

        encoded = encoded.replace("JWT ", "")
        try:
            pl: dict = jwt.decode(jwt=encoded, key=settings.public_key, algorithms=[settings.ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            AuthHTTPException.raise_http_401()
        except jwt.InvalidTokenError:
            AuthHTTPException.raise_http_400(detail="token_invalid")
        except jwt.PyJWTError as exp:
            logger.error("PyJWTError: {}", str(exp))
            AuthHTTPException.raise_http_500()
        
        payload = Payload(
            uid=pl["uid"],
            sub=pl["sub"],
            iss=pl["iss"],
            exp=pl["exp"],
            jti=pl["jti"],
            iat=pl["iat"],
            nbf=pl["nbf"],
            type=pl["type"],
        )

        return payload

    def get_access_token(self, user_id: UUID) -> str:
        token_type: str = TypeHeaderToken.ACCESS.name
        token: str = self._create_token(user_id, token_type)
        return token

    def verify_access_token(self, token: str) -> Payload:
        payload = self._decode_token(token)
        if payload.type != TypeHeaderToken.ACCESS.name:
            AuthHTTPException.raise_http_401()
        return payload


app_token = Token()
