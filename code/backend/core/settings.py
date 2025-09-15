import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RealTimeBackend"
    SERVER_NAME: str = "RealTimeBackend"
    APP_VERSION: str = "v0.1.0"
    API_V1_STR: str = "/v1"

    # Logging settings
    DEBUG: bool = False
    LOGGING_LEVEL: int = logging.INFO
    LOGGING_SAMPLING_RATIO: float = 1.0
    LOGGING_SCHEDULE_DELAY: int = 5000
    APPLICATIONINSIGHTS_CONNECTION_STRING: str


settings = Settings()
