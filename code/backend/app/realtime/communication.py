import asyncio
import base64
import json

from agents import RunContextWrapper
from agents.realtime import RealtimeAgent, RealtimeRunner
from agents.realtime.config import (
    RealtimeInputAudioTranscriptionConfig,
    RealtimeRunConfig,
    RealtimeSessionModelSettings,
    RealtimeTurnDetectionConfig,
)
from agents.realtime.model import RealtimeModelConfig
from agents.realtime.model_events import (
    RealtimeModelRawServerEvent,
)
from agents.realtime.model_inputs import RealtimeModelSendRawMessage
from app.core.settings import settings
from app.logs import setup_logging
from app.models.realtime import UserSessionContext
from app.realtime.tools import get_caller_phone_number, hang_up_call
from app.utils import _truncate_str
from fastapi import WebSocket
from starlette.websockets import WebSocketState

logger = setup_logging(__name__)


class CommunicationHandler:
    def __init__(self, websocket: WebSocket, user_session_context: UserSessionContext):
        """
        Initialize the communication handler.
        """
        self.websocket = websocket
        self.context = RunContextWrapper(user_session_context)

    async def init_model_realtime_session(self):
        """
        Initialize the model real time session.
        """
        # Create the real time agent
        real_time_agent = RealtimeAgent(
            name="Main Agent",
            instructions=settings.INSTRUCTIONS,
            tools=[get_caller_phone_number, hang_up_call],
            output_guardrails=[],
            hooks=None,
        )

        # Create the real time runner
        real_time_runner = RealtimeRunner(
            starting_agent=real_time_agent,
            config=RealtimeRunConfig(
                model_settings=RealtimeSessionModelSettings(
                    model_name=settings.REALTIME_MODEL_NAME,
                    input_audio_format="pcm16",
                    input_audio_transcription=RealtimeInputAudioTranscriptionConfig(
                        language="en",
                        model=settings.TRANSCRIPTION_MODEL_NAME,
                        prompt="",
                    ),
                    modalities=["audio"],
                    output_audio_format="pcm16",
                    speed=1.0,
                    tool_choice="auto",
                    turn_detection=RealtimeTurnDetectionConfig(
                        type="semantic_vad",
                        create_response=True,
                        eagerness="auto",
                        interrupt_response=True,
                    ),
                    voice="alloy",
                ),
                tracing_disabled=False,
            ),
        )

        # Create real time model config
        real_time_model_config = RealtimeModelConfig(
            api_key=settings.AZURE_OPENAI_API_KEY,
            url=f"wss://{settings.AZURE_OPENAI_ENDPOINT.removeprefix('https://')}openai/v1/realtime?model={settings.REALTIME_MODEL_NAME}",
        )

        # Create real time session
        logger.info(
            f"Initialize model real time session with endpoint '{settings.AZURE_OPENAI_ENDPOINT}' and model '{settings.REALTIME_MODEL_NAME}'",
            extra={"code": "INIT_MODEL_REALTIME_SESSION_START"},
        )
        session_context = await real_time_runner.run(
            context=self.context,
            model_config=real_time_model_config,
        )
        session = await session_context.__aenter__()

        # Start handling real time messages
        logger.info(
            "Starting to handle real time messages from model session",
            extra={"code": "INIT_MODEL_REALTIME_SESSION_START_PROCESSING_MESSAGES"},
        )
        receive_task = asyncio.create_task(self.process_realtime_messages())

        # Set properties
        logger.info(
            "Model real time session initialized",
            extra={"code": "INIT_MODEL_REALTIME_SESSION_INITIALIZED"},
        )

        # Start creating response to trigger model processing
        await session.model.send_event(
            event=RealtimeModelSendRawMessage(
                message={
                    "type": "response.create",
                    "other_data": {
                        "response": {
                            "instructions": (
                                "Welcome the user and say exactly, without any additions, the following message: '"
                                f"{settings.WELCOME_MESSAGE}"
                                "' now before continuing the conversation."
                            )
                        }
                    },
                },
            )
        )

        self.session = session
        self.session_context = session_context
        self.receive_task = receive_task

    async def end_session(self):
        """
        End the session.
        """
        logger.info(
            "Ending model real time session", extra={"code": "END_SESSION_START"}
        )
        await self.session_context.__aexit__(None, None, None)
        self.receive_task.cancel()
        try:
            await self.receive_task
        except asyncio.CancelledError as e:
            logger.error(
                f"Error cancelling receive task: {e}",
                extra={"code": "END_SESSION_CANCEL_RECEIVE_TASK_ERROR"},
            )
        logger.info(
            "Model real time session ended", extra={"code": "END_SESSION_SUCCESS"}
        )

    async def send_audio(self, audio: bytes):
        """
        Send audio data to the real time model session.
        """
        logger.debug(
            "Sending audio data to model session",
            extra={"code": "SEND_AUDIO_TO_MODEL_SESSION"},
        )
        await self.session.send_audio(
            audio=audio,
            commit=False,
        )

    async def receive_audio(self):
        """
        Receive audio data over the WebSocket from the client and send it to the real time model session.
        """
        while self.websocket.client_state == WebSocketState.CONNECTED:
            # Collect websocket messages
            websocket_data = await self.websocket.receive_json()

            match websocket_data.get("kind", None):
                case "AudioData":
                    logger.info(
                        "Received audio data over WebSocket",
                        extra={"code": "RECEIVE_AUDIO_AUDIO_DATA_KIND_RECEIVED"},
                    )

                    # Extract audio data
                    audio_data_base64 = websocket_data.get("audioData", {}).get(
                        "data", None
                    )

                    # Convert base64 string to bytes
                    audio_data_bytes = base64.b64decode(audio_data_base64)

                    # Send audio data to the real time model session
                    if audio_data_bytes:
                        await self.send_audio(audio=audio_data_bytes)

                case "DtmfData":
                    logger.info(
                        "Received DTMF data over WebSocket",
                        extra={"code": "RECEIVE_AUDIO_DTMF_DATA_KIND_RECEIVED"},
                    )

                    # Extract DTMF data
                    dtmf_data = websocket_data.get("dtmfData", {}).get("data", None)
                    logger.debug(
                        "DTMF data received",
                        extra={
                            "code": "RECEIVE_AUDIO_DTMF_DATA_KIND_VALUE_RECEIVED",
                            "dtmf_data_present": dtmf_data is not None,
                            "dtmf_data_length": (
                                len(str(dtmf_data)) if dtmf_data is not None else 0
                            ),
                        },
                    )

                case _:
                    logger.warning(
                        f"Unknown data kind received over WebSocket: {websocket_data.get('kind', None)}",
                        extra={"code": "RECEIVE_AUDIO_UNKNOWN_DATA_KIND_RECEIVED"},
                    )

    async def return_audio(self, audio: bytes):
        """
        Return audio data to the client over the WebSocket.
        """
        logger.debug(
            "Audio received from the model, sending to ACS client over WebSocket",
            extra={"code": "RETURN_AUDIO"},
        )
        await self.websocket.send_text(
            json.dumps(
                {
                    "Kind": "AudioData",
                    "AudioData": {"Data": base64.b64encode(audio).decode("utf-8")},
                }
            )
        )

    async def interrupt_audio(self):
        """
        Interrupt audio data to the client over the WebSocket.
        """
        logger.debug("Interrupt audio in ACS", extra={"code": "INTERRUPT_AUDIO"})
        await self.websocket.send_text(
            json.dumps(
                {
                    "Kind": "StopAudio",
                    "AudioData": None,
                    "StopAudio": {},
                }
            )
        )

    async def process_realtime_messages(self):
        """
        Process real time messages from the model session.
        """
        try:
            logger.debug(
                "Handling realtime messages",
                extra={"code": "PROCESS_REALTIME_MESSAGES_START"},
            )
            async for event in self.session:
                logger.debug(
                    f"Event received: {event.type}",
                    extra={"code": "PROCESS_REALTIME_MESSAGES_EVENT_RECEIVED"},
                )
                try:
                    if settings.DEBUG and event.data:
                        truncated_data = _truncate_str(str(event.data), 200)
                        logger.debug(
                            f"Data: '{truncated_data}'",
                            extra={"code": "PROCESS_REALTIME_MESSAGES_EVENT_DATA"},
                        )
                        logger.debug(
                            f"Event Info: '{event.info}'",
                            extra={"code": "PROCESS_REALTIME_MESSAGES_EVENT_INFO"},
                        )

                except Exception as e:
                    logger.warning(
                        f"Error processing events data: {e}",
                        extra={"code": "PROCESS_REALTIME_MESSAGES_EVENT_DATA_ERROR"},
                    )

                if event.type == "agent_start":
                    pass
                elif event.type == "agent_end":
                    pass
                elif event.type == "handoff":
                    pass
                elif event.type == "tool_start":
                    logger.info(
                        f"Tool call start detected. Agent: '{event.agent}', Tool Name: '{event.tool.name}', Tool arguments: '{event.arguments}'",
                        extra={"code": "PROCESS_REALTIME_MESSAGES_TOOL_START_RECEIVED"},
                    )
                elif event.type == "tool_end":
                    logger.info(
                        f"Tool call end detected. Agent: '{event.agent}', Tool Name: '{event.tool.name}', Tool arguments: '{event.arguments}', Tool output: '{event.output}'",
                        extra={"code": "PROCESS_REALTIME_MESSAGES_TOOL_END_RECEIVED"},
                    )
                elif event.type == "audio":
                    if event.audio and event.audio.data:
                        await self.return_audio(event.audio.data)
                elif event.type == "audio_interrupted":
                    await self.interrupt_audio()
                elif event.type == "audio_end":
                    pass
                elif event.type == "history_updated":
                    pass
                elif event.type == "history_added":
                    pass
                elif event.type == "guardrail_tripped":
                    pass
                elif event.type == "raw_model_event":
                    # Filter on raw model server events
                    if event.data and isinstance(
                        event.data, RealtimeModelRawServerEvent
                    ):
                        # Get raw event type
                        raw_event_type = event.data.data.get("type", None)
                        logger.info(
                            f"Raw event type: {raw_event_type}",
                            extra={
                                "code": "PROCESS_REALTIME_MESSAGES_RAW_MODEL_EVENT_RECEIVED"
                            },
                        )

                        if raw_event_type == "response.output_audio_transcript.done":
                            logger.info(
                                f"Model output transcription completed: '{event.data.data.get('transcript', None)}'",
                                extra={
                                    "code": "PROCESS_REALTIME_MESSAGES_OUTPUT_AUDIO_TRANSCRIPT_DONE_RECEIVED"
                                },
                            )
                        elif (
                            raw_event_type
                            == "conversation.item.input_audio_transcription.completed"
                        ):
                            logger.info(
                                f"User input transcription completed: {event.data.data.get('transcript', None)}",
                                extra={
                                    "code": "PROCESS_REALTIME_MESSAGES_INPUT_AUDIO_TRANSCRIPTION_COMPLETED_RECEIVED"
                                },
                            )

                elif event.type == "error":
                    logger.error(
                        f"Error event received from model: {event.error}",
                        exc_info=True,
                        extra={"code": "PROCESS_REALTIME_MESSAGES_ERROR_RECEIVED"},
                    )
                elif event.type == "input_audio_timeout_triggered":
                    pass
                else:
                    pass
        except Exception as e:
            logger.error(
                f"Breaking error processing events for session: {e}",
                exc_info=True,
                extra={"code": "PROCESS_REALTIME_MESSAGES_EXCEPTION"},
            )
            raise e
