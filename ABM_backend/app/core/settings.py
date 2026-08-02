from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("DATABASE_URL no puede estar vacío.")
        return value


class SecuritySettings(BaseSettings):
    SERVICE_API_KEY: str

    @field_validator("SERVICE_API_KEY")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("SERVICE_API_KEY no puede estar vacío.")
        return value


class StorageSettings(BaseSettings):
    GOOGLE_CLOUD_PROJECT_ID: str

    GOOGLE_CLOUD_BUCKET: str

    GOOGLE_APPLICATION_CREDENTIALS: str

    @field_validator(
        "GOOGLE_CLOUD_PROJECT_ID",
        "GOOGLE_CLOUD_BUCKET",
        "GOOGLE_APPLICATION_CREDENTIALS",
    )
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value


class AIServiceSettings(BaseSettings):
    AI_SERVICE_URL: str
    AI_SERVICE_API_KEY: str
    AI_SERVICE_TIMEOUT: int = 60

    @field_validator("AI_SERVICE_URL", "AI_SERVICE_API_KEY")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value


class AppSettings(BaseSettings):
    PROJECT_NAME: str = "Vehicle Management API"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
class DamageDetectionSettings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_DAMAGE_MODEL: str = "gpt-4o-mini"

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("OPENAI_API_KEY no puede estar vacío.")
        return value


class Settings(
    DatabaseSettings,
    SecuritySettings,
    StorageSettings,
    AIServiceSettings,
    DamageDetectionSettings,
    AppSettings,
):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Devuelve una única instancia de Settings durante toda la vida de la aplicación.
    """
    return Settings()


settings = get_settings()