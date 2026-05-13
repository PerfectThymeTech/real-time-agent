from typing import Annotated, Optional

from app.calls.process import (
    process_callback_event,
    process_incoming_call_event,
)
from app.calls.validate import (
    validate_callback_authorization,
    validate_incoming_call_authorization,
)
from app.core.settings import settings
from app.logs import setup_logging
from app.models.calls import ValidationResponse
from fastapi import APIRouter, Depends, Header, HTTPException, Query

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    path="/incoming",
    name="IncomingCall",
)
async def post_incoming_call(
    events: list[dict],
    token_query: Annotated[str | None, Query(alias="token")] = None,
) -> Optional[ValidationResponse]:
    """
    Receives incoming call events from Azure Communication Services.
    """
    logger.info(
        "Received Incoming Call Event", extra={"code": "REQUEST_INCOMING_CALL_RECEIVED"}
    )
    logger.debug(
        "Received incoming call token",
        extra={
            "code": "REQUEST_INCOMING_CALL_TOKEN_RECEIVED",
            "token_present": bool(token_query),
        },
    )

    # Validate the token query parameter to ensure the request is coming from a trusted source
    if not token_query or not validate_incoming_call_authorization(
        token_query=token_query,
        acs_token_query=settings.ACS_TOKEN_QUERY,
    ):
        logger.warning(
            "Unauthorized incoming call event received",
            extra={"code": "REQUEST_INCOMING_CALL_UNAUTHORIZED"},
        )
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Process the incoming call event and determine if the call should be accepted or rejected
    result = process_incoming_call_event(events=events)

    if result:
        return result


@router.post(
    path="/callbacks/{contextId}",
    name="CallbackContext",
)
async def post_callback_context(
    contextId: str,
    events: list[dict],
    authorization_header: Annotated[str | None, Header(alias="authorization")] = None,
) -> None:
    """
    Receives callback events for a call from Azure Communication Services.
    """
    logger.info(
        "Received Callback Context Event for a Call",
        extra={"code": "REQUEST_CALLBACK_CONTEXT_RECEIVED"},
    )

    # Validate the authorization header to ensure the request is coming from a trusted source
    if not authorization_header or not validate_callback_authorization(
        authorization_header=authorization_header,
        acs_resource_id=settings.ACS_RESOURCE_ID,
    ):
        logger.warning(
            "Unauthorized callback event received",
            extra={"code": "REQUEST_CALLBACK_CONTEXT_UNAUTHORIZED"},
        )
        raise HTTPException(status_code=401, detail="Unauthorized")

    await process_callback_event(context_id=contextId, events=events)
