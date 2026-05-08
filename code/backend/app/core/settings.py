import logging

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General settings
    PROJECT_NAME: str = "RealTimeBackend"
    PROJECT_DESCRIPTION: str = "Backend API for Real-Time Agent"
    SERVER_NAME: str = "RealTimeBackend"
    APP_VERSION: str = "v0.1.0"
    API_V1_STR: str = "/v1"

    # Deployment settings
    APP_BASE_URL: str = Field(
        ..., alias=AliasChoices("BASE_URL", "CONTAINER_APP_HOSTNAME")
    )
    APP_CONTAINER_NAME: str = Field(
        ..., alias=AliasChoices("CONTAINER_NAME", "CONTAINER_APP_NAME")
    )
    APP_CONTAINER_REVISION: str = Field(
        ..., alias=AliasChoices("CONTAINER_REVISION", "CONTAINER_APP_REVISION")
    )
    APP_NAMESPACE: str = Field(
        ..., alias=AliasChoices("NAMESPACE", "CONTAINER_APP_ENV_DNS_SUFFIX")
    )
    APP_HOME_DIRECTORY: str = "./"

    # Logging settings
    DEBUG: bool = False
    LOGGING_LEVEL: int = logging.INFO
    LOGGING_SAMPLING_RATIO: float = 1.0
    LOGGING_SCHEDULE_DELAY: int = 5000
    LOGGING_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(module)-8.8s] %(message)s"
    APPLICATIONINSIGHTS_CONNECTION_STRING: str
    APPLICATIONINSIGHTS_AUTHENTICATION_STRING: str = None

    # Identity settings
    MANAGED_IDENTITY_CLIENT_ID: str = ""

    # Azure Communication Services settings
    ACS_CONNECTION_STRING: str

    # Azure Open AI settings
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
