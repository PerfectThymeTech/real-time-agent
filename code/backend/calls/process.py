from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

from azure.communication.callautomation import (
    AudioFormat,
    CallAutomationClient,
    MediaStreamingAudioChannelType,
    MediaStreamingContentType,
    MediaStreamingOptions,
    StreamingTransportType,
)
from azure.core.exceptions import HttpResponseError
from azure.eventgrid import EventGridEvent, SystemEventNames
from core.settings import settings
from logs import setup_logging
from models.calls import ValidationResponse

logger = setup_logging(__name__)


def get_acs_client() -> CallAutomationClient:
    """
    Returns a CallAutomationClient to answer phone calls received from Azure Communication Services.
    """
    client = CallAutomationClient.from_connection_string(
        conn_str=settings.ACS_CONNECTION_STRING
    )
    return client


def process_incoming_call_event(
    events: list[dict], client: CallAutomationClient
) -> Any:
    """
    Processes an incoming call event.
    """
    # Set callback base url
    callback_events_uri_base = f"https://{settings.BASE_URL}/v1/calls/callbacks"
    websocket_url = f"wss://{settings.BASE_URL}/v1/realtime/realtime"
    logger.info(f"Setting callback events base URI to: {callback_events_uri_base}")

    for event in events:
        event_grid_event = EventGridEvent.from_dict(event)
        logger.info(f"Processing event: {event_grid_event.event_type}")

        if event_grid_event.event_type == SystemEventNames.AcsIncomingCallEventName:
            logger.info("Incoming call event received.")

            # Parse event data
            caller_id = (
                event_grid_event.data.get("from", {"phoneNumber": {"value": ""}})
                .get("phoneNumber", {"value": ""})
                .get("value")
                if event_grid_event.data.get("from", {"kind": ""}).get("kind")
                == "phoneNumber"
                else event_grid_event.data.get("from", {"rawId": ""}).get("rawId")
            )
            incoming_call_context = event_grid_event.data.get("incomingCallContext")
            guid = uuid4()

            # Answer the call
            query_parameters = urlencode(
                {
                    "callerId": caller_id,
                }
            )
            callback_events_uri = (
                f"{callback_events_uri_base}/{guid}?{query_parameters}"
            )

            try:
                answer_call_result = client.answer_call(
                    incoming_call_context=incoming_call_context,
                    callback_url=callback_events_uri,
                    operation_context="incomingCall",
                    media_streaming=MediaStreamingOptions(
                        transport_url=websocket_url,
                        transport_type=StreamingTransportType.WEBSOCKET,
                        content_type=MediaStreamingContentType.AUDIO,
                        audio_channel_type=MediaStreamingAudioChannelType.MIXED,
                        start_media_streaming=True,
                        enable_bidirectional=True,
                        audio_format=AudioFormat.PCM24_K_MONO,
                    ),
                )
                logger.info(
                    f"Answered call with Call Connection ID '{answer_call_result.call_connection_id}' and correlation ID '{answer_call_result.correlation_id}'."
                )
            except HttpResponseError as e:
                logger.error(f"Failed to answer call: {e.message}")
                raise e

        elif (
            event_grid_event.event_type
            == SystemEventNames.EventGridSubscriptionValidationEventName
        ):
            logger.info("Event subscription validation event received.")

            # Parse event data
            validation_code = event_grid_event.data.get("validationCode")

            # Return the validation response
            validation_response = ValidationResponse(
                validation_response=validation_code
            )
            return validation_response


async def process_callback_event(
    context_id: str, events: list[dict], client: CallAutomationClient
) -> None:
    """
    Processes a callback event for a call.
    """
    for event in events:
        # Get event data
        event_type = event.get("type")
        event_data = event.get("data", {})

        logger.info(
            f"Processing event. Context ID: {context_id}, Event Type: {event_type}, Correlation ID: {event_data.get('correlationId')}, Call Connection ID: {event_data.get('callConnectionId')}"
        )

        match event_type:
            case "Microsoft.Communication.CallConnected":
                logger.info(
                    f"Call connected event received for Context ID: {context_id}"
                )

                # Get call connection properties
                call_connection = client.get_call_connection(
                    call_connection_id=event_data.get("callConnectionId")
                )
                call_properties = await call_connection.get_call_properties()
                logger.info(
                    f"MediaStreamingSubscription: {getattr(call_properties, 'media_streaming_subscription', 'N/A')}"
                )

            case (
                "Microsoft.Communication.MediaStreamingStarted"
                | "Microsoft.Communication.MediaStreamingStopped"
            ):
                logger.info(
                    f"Media streaming event received for Context ID: {context_id}"
                )

                # Get Media Streaming Update
                media_streaming_update = event_data.get("mediaStreamingUpdate", {})
                logger.info(
                    f"Media Streaming Content Type: {media_streaming_update.get('contentType')}, Media Streaming Status: {media_streaming_update.get('mediaStreamingStatus')}, Media Streaming Details: {media_streaming_update.get('mediaStreamingStatusDetails')}"
                )

            case "Microsoft.Communication.MediaStreamingFailed":
                logger.info(
                    f"Media streaming failed event received for Context ID: {context_id}"
                )

                # Get Result Information
                result_information = event_data.get("resultInformation", {})
                logger.info(
                    f"Code: {result_information.get('code')}, Subcode: {result_information.get('subCode')}"
                )

            case "Microsoft.Communication.CallDisconnected":
                logger.info(
                    f"Call disconnected event received for Context ID: {context_id}"
                )

            case _:
                logger.warning(
                    f"Unhandled event type: {event_type} for Context ID: {context_id}"
                )
    return None
