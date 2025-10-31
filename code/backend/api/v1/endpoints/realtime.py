from typing import Any

from fastapi import APIRouter, Depends, WebSocket
from utils import setup_logging
from calls.utils import get_acs_client

logger = setup_logging(__name__)

router = APIRouter()


@router.websocket(
    path="/realtime",
    name="realtime",
    dependencies=[Depends(get_acs_client)],
)
async def realtime(websocket: WebSocket, acs_client=Depends(get_acs_client)) -> Any:
    """
    WebSocket endpoint for real-time communication.
    """
    logger.info("Received Websocket Connection")
    await websocket.accept()
    await websocket.send_text(f"WebSocket connection established")
