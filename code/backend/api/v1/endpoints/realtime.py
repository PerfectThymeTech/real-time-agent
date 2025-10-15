from typing import Any

from fastapi import APIRouter, WebSocket, Depends
from utils import setup_logging

logger = setup_logging(__name__)

router = APIRouter()


@router.websocket(
    path="/realtime",
    name="realtime",
    # dependencies=[Depends(TODO)],
)
async def realtime(websocket: WebSocket) -> Any:
    logger.info("Received Websocket Connection")
    await websocket.accept()
    await websocket.send_text(f"WebSocket connection established")
