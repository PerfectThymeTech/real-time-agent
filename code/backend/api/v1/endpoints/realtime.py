from contextlib import AsyncExitStack
from typing import Annotated, Any

from calls.utils import get_acs_client
from fastapi import APIRouter, Depends, Header, WebSocket
from utils import setup_logging

logger = setup_logging(__name__)

router = APIRouter()


@router.websocket(
    path="/realtime",
    name="realtime",
    dependencies=[Depends(get_acs_client)],
)
async def realtime(
    websocket: WebSocket,
    call_connection_id: Annotated[
        str | None, Header(alias="x-ms-call-connection-id")
    ] = None,
    acs_client=Depends(get_acs_client),
) -> Any:
    """
    WebSocket endpoint for real-time communication.
    """
    logger.info("Received Websocket Connection")

    # Accept the WebSocket connection
    await websocket.accept()

    if not call_connection_id:
        logger.warning(
            "Missing x-ms-call-connection-id header indicates direct connection not coming through ACS."
        )

    async with AsyncExitStack() as stack:
        pass
