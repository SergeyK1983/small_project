from pathlib import Path

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

    # App
    APPLICATION: str = Field(alias="SMPR_APPLICATION")
    ALLOWED_HOST: str = Field(alias="SMPR_ALLOWED_HOST")
    SECRETS_DIR: str = Field(alias="SMPR_SECRETS_DIR", default="")
    ALLOW_ORIGINS: list[str] = Field(alias="SMPR_ALLOW_ORIGINS")
    ALLOW_HEADERS: list[str] = Field(alias="SMPR_ALLOW_HEADERS")
    ALLOW_METHODS: list[str] = Field(alias="SMPR_ALLOW_METHODS")

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


settings = Settings() # type: ignore
