import logging

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


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


settings = Settings()
