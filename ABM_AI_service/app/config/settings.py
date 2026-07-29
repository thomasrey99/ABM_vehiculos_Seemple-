from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Literal


class Settings(BaseSettings):
    SERVICE_API_KEY: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    MODEL: str
    COLLECTION_NAME: str = "vehicles-images"
    CLIP_VECTOR_SIZE: int = 512
    VECTOR_DISTANCE: Literal["Cosine", "Euclidean", "Dot"] = "Cosine"

    # Reconocimiento automático de patentes (ANPR)
    PLATE_MIN_CONFIDENCE: float = 0.90
    PLATE_DETECTOR_MODEL: str = "yolo-v9-t-384-license-plate-end2end"
    PLATE_OCR_MODEL: str = "cct-xs-v2-global-model"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @field_validator("SERVICE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY", "MODEL")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """
        Validador de configuración que levanta error al iniciar el servicio si te falta alguna credencial en el archivo .env.
        """
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío")
        return v


settings = Settings()