from typing import TYPE_CHECKING

from src.auth.utils.hasher import hasher


if TYPE_CHECKING:
    from src.auth.utils.hasher import Argon2Hasher


class Password:

    def __init__(self, hasher: "Argon2Hasher"):
        self.hasher = hasher

    def hashing_password(self, pwd: str) -> str:        
        hash_pwd: str = self.hasher.hashing_password(password=pwd)
        return hash_pwd

    def verify_password(self, hashed: str, password: str) -> bool:
        verify: bool = self.hasher.verify(hashed=hashed, password=password)
        return verify

    def check_rehash_password(self, hashed_pwd: str) -> bool:
        return self.hasher.needs_rehash(hashed_pwd)

    def change_password(self, ): ...

    def reset_password(self): ...


password = Password(hasher)
