from contextlib import AsyncExitStack
from typing import Annotated, Any

from app.calls.validate import validate_websocket_authorization
from app.core.settings import settings
from app.logs import setup_logging
from app.models.realtime import UserSessionContext
from app.realtime.communication import CommunicationHandler
from fastapi import APIRouter, Depends, Header, WebSocket, WebSocketDisconnect

logger = setup_logging(__name__)

router = APIRouter()


@router.websocket(
    path="/realtime",
    name="realtime",
)
async def realtime(
    websocket: WebSocket,
    authorization_header: Annotated[str | None, Header(alias="authorization")] = None,
    call_connection_id_header: Annotated[
        str | None, Header(alias="x-ms-call-connection-id")
    ] = None,
) -> Any:
    """
    WebSocket endpoint for real-time communication.
    """
    logger.info(
        f"Received Websocket Connection with call connection ID: {call_connection_id_header}",
        extra={"code": "REQUEST_REALTIME_RECEIVED"}
    )

    # Validate the authorization header to ensure the request is coming from a trusted source
    if not authorization_header or not validate_websocket_authorization(
        authorization_header=authorization_header,
        acs_resource_id=settings.ACS_RESOURCE_ID,
    ):
        logger.warning(
            "Unauthorized WebSocket connection attempt",
            extra={"code": "REQUEST_REALTIME_UNAUTHORIZED"},
        )
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Validate the presence of the call connection ID header
    if not call_connection_id_header:
        logger.warning(
            "Missing call connection ID header in WebSocket connection attempt",
            extra={"code": "REQUEST_REALTIME_MISSING_CALL_CONNECTION_ID"},
        )
        await websocket.close(code=1008, reason="Missing call connection ID header")
        return

    # Accept the WebSocket connection
    await websocket.accept()

    # Create user session context
    call_connection_id_header = websocket.headers.get("x-ms-call-connection-id")
    user_session_context = UserSessionContext(
        call_connection_id=call_connection_id_header,
    )

    async with AsyncExitStack() as stack:
        # Create and init communication handler
        comm_handler = CommunicationHandler(
            websocket=websocket, user_session_context=user_session_context
        )
        await comm_handler.init_model_realtime_session()

        # Init variable
        error_occurred = False

        try:
            # Receive audio data over websocket
            await comm_handler.receive_audio()

        except WebSocketDisconnect as e:
            logger.warning(
                f"WebSocket disconnected by client: {e}",
                exc_info=True,
                extra={"code": "REQUEST_REALTIME_WEBSOCKET_DISCONNECTED_BY_CLIENT"},
            )
            error_occurred = True

        except Exception as e:
            logger.error(
                f"Unexpected exception occurred: {e}",
                exc_info=True,
                extra={"code": "REQUEST_REALTIME_UNEXPECTED_EXCEPTION"},
            )
            error_occurred = True

            # End websocket connection
            await websocket.close(code=1011, reason="Internal server error")

        finally:
            # Close session
            await comm_handler.end_session()

            # End websocket connection
            if not error_occurred:
                logger.info("WebSocket connection closed normally, ending session.")
                await websocket.close(code=1000, reason="Ending connection normally")
