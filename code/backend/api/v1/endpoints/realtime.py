import base64
from contextlib import AsyncExitStack
from typing import Annotated, Any

from calls.utils import get_acs_client
from fastapi import APIRouter, Depends, Header, WebSocket
from logs import setup_logging
from realtime.communication import CommunicationHandler
from starlette.websockets import WebSocketState

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
        # Create and init communication handler
        comm_handler = CommunicationHandler(websocket=websocket)
        await comm_handler.init_model_realtime_session()
        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                # Collect websocket messages
                message = await websocket.receive_json()

                match message.get("type", None):
                    case "AudioData":
                        logger.info("Received audio data over WebSocket")

                        # Extract audio data
                        audio_data_base64 = message.get("audioData", {}).get(
                            "data", None
                        )

                        # Convert base64 string to bytes
                        audio_data_bytes = base64.b64decode(audio_data_base64)

                        # Send audio data to the real time model session
                        if audio_data_bytes:
                            await comm_handler.send_audio(audio=audio_data_bytes)

                    case _:
                        logger.warning(
                            f"Unknown data type received over WebSocket: {message.get('type', None)}"
                        )

        except Exception as e:
            logger.error(f"Unexpected exception occured: {e}", exc_info=e)

        finally:
            # Close session
            await comm_handler.end_session()
