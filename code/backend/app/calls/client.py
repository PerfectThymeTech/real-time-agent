from app.core.settings import settings
from app.logs import setup_logging
from azure.communication.callautomation.aio import (
    CallAutomationClient,
)

logger = setup_logging(__name__)


def get_acs_client() -> CallAutomationClient:
    """
    Returns a CallAutomationClient to answer phone calls received from Azure Communication Services.
    """
    logger.info(
        "Creating CallAutomationClient for Azure Communication Services",
        extra={"code": "GET_ACS_CLIENT_CREATION"},
    )
    client = CallAutomationClient.from_connection_string(
        conn_str=settings.ACS_CONNECTION_STRING
    )
    return client


ACS_CLIENT = get_acs_client()
