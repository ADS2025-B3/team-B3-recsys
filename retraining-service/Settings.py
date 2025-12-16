from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = Field(default=5432)
    
    # Backend
    BACKEND_URL: str
    
    # MLflow
    MLFLOW_TRACKING_URI: str
    MLFLOW_TRACKING_USERNAME: str
    MLFLOW_TRACKING_PASSWORD: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Convertir automáticamente strings de env vars a tipos correctos
        coerce_numbers_to_str = False
        # Si quieres permitir campos extra en el futuro:
        # extra = "allow"


settings = Settings()