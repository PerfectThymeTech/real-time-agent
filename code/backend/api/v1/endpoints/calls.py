from typing import Any

from calls.utils import get_acs_client
from fastapi import APIRouter, WebSocket, Depends
from utils import setup_logging

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    path="/incoming",
    name="IncomingCall",
    # dependencies=[Depends(TODO)],
)
async def post_incoming_call(events: list[dict], acs_client=Depends(get_acs_client)) -> Any:
    logger.info("Received Incoming Call Event")
    pass


@router.post(
    path="/callbacks/{contextId}",
    name="CallbackContext",
    # dependencies=[Depends(TODO)],
)
async def post_callback_context(contextId: str, events: list[dict], acs_client=Depends(get_acs_client)) -> Any:
    logger.info("Received Incoming Call Callback Context Event")
    pass
