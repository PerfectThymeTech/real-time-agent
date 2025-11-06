import logging

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General settings
    PROJECT_NAME: str = "RealTimeBackend"
    SERVER_NAME: str = "RealTimeBackend"
    APP_VERSION: str = "v0.1.0"
    API_V1_STR: str = "/v1"

    # Deployment settings
    BASE_URL: str = Field(..., alias=AliasChoices("BASE_URL", "CONTAINER_APP_HOSTNAME"))

    # Azure Communication Services settings
    ACS_CONNECTION_STRING: str

    # Logging settings
    DEBUG: bool = False
    LOGGING_LEVEL: int = logging.INFO
    LOGGING_SAMPLING_RATIO: float = 1.0
    LOGGING_SCHEDULE_DELAY: int = 5000
    LOGGING_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(module)-8.8s] %(message)s"
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = None

    # Open AI settings
    INSTRUCTIONS: str
    REALTIME_MODEL_NAME: str = Field(
        default="gpt-realtime",
        alias=AliasChoices("REALTIME_MODEL_NAME", "AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
    TRANSCRIPTION_MODEL_NAME: str = "gpt-4o-transcribe"
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
