from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError, VerificationError, InvalidHashError

from src.core.logger import logger


class HasherError(Exception):
    pass


class Argon2Hasher:

    def __init__(self):
        self._hasher = PasswordHasher()

    def hashing_password(self, password: str) -> str:
        try:
            return self._hasher.hash(password)
        except HashingError as exp:
            logger.error("Password hashing error: {}", exp.args[0])
            raise HasherError()

    def verify(self, hashed: str, password: str) -> bool:
        try:
            return self._hasher.verify(hashed, password)
        except (VerifyMismatchError, VerificationError):
            return False
        except InvalidHashError as exp:
            logger.error("Verify password error: InvalidHashError, {}", str(exp))
            raise HasherError()

    def needs_rehash(self, hashed: str) -> bool:
        return self._hasher.check_needs_rehash(hashed)


hasher = Argon2Hasher()
