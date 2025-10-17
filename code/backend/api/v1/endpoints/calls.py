from typing import Any

from calls.utils import get_acs_client, process_incoming_call_event
from fastapi import APIRouter, Depends
from utils import setup_logging

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    path="/incoming",
    name="IncomingCall",
    dependencies=[Depends(get_acs_client)],
)
async def post_incoming_call(
    events: list[dict], acs_client=Depends(get_acs_client)
) -> Any:
    """
    Receives incoming call events from Azure Communication Services.
    """
    logger.info("Received Incoming Call Event")
    result = process_incoming_call_event(events=events, client=acs_client)

    if result:
        return result


@router.post(
    path="/callbacks/{contextId}",
    name="CallbackContext",
    dependencies=[Depends(get_acs_client)],
)
async def post_callback_context(
    contextId: str, events: list[dict], acs_client=Depends(get_acs_client)
) -> Any:
    """
    Receives callback events for a call from Azure Communication Services.
    """
    logger.info("Received Callback Context Event for a Call")
    pass
