from pathlib import Path

from cryptography.hazmat.primitives import serialization
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings, case_sensitive=True):

    # database
    POSTGRES_NAME: str = Field(alias="SMPR_POSTGRES_NAME")
    POSTGRES_USER: str = Field(alias="SMPR_POSTGRES_USER")
    POSTGRES_PASS_FILE: str = Field(alias="SMPR_POSTGRES_PASS_FILE")
    POSTGRES_HOST: str = Field(alias="SMPR_POSTGRES_HOST")
    POSTGRES_PORT: str = Field(alias="SMPR_POSTGRES_PORT")
    ECHO: bool = Field(alias="SMPR_ECHO")

    # auth
    PASSWORD_FILE: str = Field(alias="SMPR_PASSWORD_FILE")
    ALGORITHM: str = Field(alias="SMPR_ALGORITHM")
    PRIVATE_KEY: str = Field(alias="SMPR_PRIVATE_KEY")
    PUBLIC_KEY: str = Field(alias="SMPR_PUBLIC_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="SMPR_ACCESS_TOKEN_EXPIRE_MINUTES")

    # App
    APPLICATION: str = Field(alias="SMPR_APPLICATION")
    ALLOWED_HOST: list[str] = Field(alias="SMPR_ALLOWED_HOST")
    SECRETS_DIR: str = Field(alias="SMPR_SECRETS_DIR", default="")
    ALLOW_ORIGINS: list[str] = Field(alias="SMPR_ALLOW_ORIGINS")
    ALLOW_HEADERS: list[str] = Field(alias="SMPR_ALLOW_HEADERS")
    ALLOW_METHODS: list[str] = Field(alias="SMPR_ALLOW_METHODS")
    PAYMENT_PSW_FILE: str = Field(alias="SMPR_PAYMENT_PSW_FILE")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def _get_base_path(self):
        base_path = Path(self.SECRETS_DIR) if self.SECRETS_DIR else BASE_DIR
        return base_path
    
    def _get_db_pass(self) -> str:
        base_path = self._get_base_path()
        with open(base_path / self.POSTGRES_PASS_FILE, "r") as f:
            password = f.read()
        return password

    @property
    def async_postgresql_url(self) -> str:
        db_pass = self._get_db_pass()
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{db_pass}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"

    @property
    def async_test_postgresql_url(self) -> str:
        """ Для тестов """
        db_pass = self._get_db_pass()
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{db_pass}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/test_db"
    
    @property
    def public_key(self):
        base_path = self._get_base_path()
        with open(base_path / self.PUBLIC_KEY, "rb") as f:
            key = f.read()
        return key

    @property
    def private_key(self):
        base_path = self._get_base_path()
        with open(base_path / self.PRIVATE_KEY, "rb") as f:
            key = f.read()

        with open(base_path / self.PASSWORD_FILE, "rb") as f:
            password = f.read()

        private_key = serialization.load_pem_private_key(
            key,
            password=password
        )
        return private_key
    
    @property
    def payment_key(self):
        base_path = self._get_base_path()

        with open(base_path / self.PAYMENT_PSW_FILE, "r") as f:
            password = f.read()
        
        return password


settings = Settings() # type: ignore
