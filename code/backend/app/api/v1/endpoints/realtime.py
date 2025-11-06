from contextlib import AsyncExitStack
from typing import Annotated, Any

from app.calls.process import get_acs_client
from fastapi import APIRouter, Depends, Header, WebSocket
from app.logs import setup_logging
from app.realtime.communication import CommunicationHandler

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

        # Init variable
        error_occurred = False

        try:
            # Receive audio data over websocket
            await comm_handler.receive_audio()

        except Exception as e:
            logger.error(f"Unexpected exception occurred: {e}", exc_info=e)
            error_occurred = True

            # End websocket connection
            await websocket.close(code=1011, reason="Internal server error")

        finally:
            # Close session
            await comm_handler.end_session()

            # End websocket connection
            if not error_occurred:
                await websocket.close(code=1000, reason="Ending connection normally")
