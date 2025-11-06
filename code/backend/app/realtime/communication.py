import asyncio
import base64
import json

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
from app.core.settings import settings
from fastapi import WebSocket
from app.logs import setup_logging
from starlette.websockets import WebSocketState
from app.utils import _truncate_str

logger = setup_logging(__name__)


class CommunicationHandler:
    def __init__(self, websocket: WebSocket):
        """
        Initialize the communication handler.
        """
        self.websocket = websocket

    async def init_model_realtime_session(self):
        """
        Initialize the model real time session.
        """
        # Create the real time agent
        real_time_agent = RealtimeAgent(
            name="Main Agent",
            instructions=settings.INSTRUCTIONS,
            tools=[],
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
            url=f"wss://{settings.AZURE_OPENAI_ENDPOINT}openai/v1/realtime?model={settings.REALTIME_MODEL_NAME}",
        )

        # Create real time session
        logger.info(
            f"Initialize model real time session with endpoint '{settings.AZURE_OPENAI_ENDPOINT}' and model '{settings.REALTIME_MODEL_NAME}'"
        )
        session_context = await real_time_runner.run(
            context=None,
            model_config=real_time_model_config,
        )
        session = await session_context.__aenter__()

        # Start handling real time messages
        logger.info("Starting to handle real time messages from model session")
        receive_task = asyncio.create_task(self.process_realtime_messages())

        # Set properties
        logger.info("Model real time session initialized")
        self.session = session
        self.session_context = session_context
        self.receive_task = receive_task

    async def end_session(self):
        """
        End the session.
        """
        await self.session_context.__aexit__(None, None, None)
        try:
            self.receive_task.cancel()
        except asyncio.CancelledError as e:
            logger.error(f"Error cancelling receive task: {e}")

    async def send_audio(self, audio: bytes):
        """
        Send audio data to the real time model session.
        """
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

            match websocket_data.get("type", None):
                case "AudioData":
                    logger.info("Received audio data over WebSocket")

                    # Extract audio data
                    audio_data_base64 = websocket_data.get("audioData", {}).get(
                        "data", None
                    )

                    # Convert base64 string to bytes
                    audio_data_bytes = base64.b64decode(audio_data_base64)

                    # Send audio data to the real time model session
                    if audio_data_bytes:
                        await self.send_audio(audio=audio_data_bytes)

                case _:
                    logger.warning(
                        f"Unknown data type received over WebSocket: {websocket_data.get('type', None)}"
                    )

    async def return_audio(self, audio: bytes):
        """
        Return audio data to the client over the WebSocket.
        """
        logger.debug("Audio received from the model, sending to ACS client")
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
        logger.debug("Interrupt audio in ACS")
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
            logger.info("Handling realtime messages")
            async for event in self.session:
                logger.info(f"Event received: {event.type}")
                try:
                    if event.data:
                        truncated_data = _truncate_str(str(event.data), 200)
                        logger.debug(f"Data: '{truncated_data}'")
                except Exception as e:
                    logger.warning(f"Error processing events data: {e}")

                if event.type == "agent_start":
                    pass
                elif event.type == "agent_end":
                    pass
                elif event.type == "handoff":
                    pass
                elif event.type == "tool_start":
                    logger.info(f"Tool Call: {event.tool.name} - {event.info}")
                elif event.type == "tool_end":
                    pass
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
                        logger.info(f"Raw event type: {raw_event_type}")

                        if raw_event_type == "response.output_audio_transcript.done":
                            logger.info(
                                f"Model output transcription completed: '{event.data.data.get('transcript', None)}'"
                            )
                        elif (
                            raw_event_type
                            == "conversation.item.input_audio_transcription.completed"
                        ):
                            logger.info(
                                f"User input transcription completed: {event.data.data.get('transcript', None)}"
                            )

                elif event.type == "error":
                    logger.error(f"Error event received from model: {event.error}")
                elif event.type == "input_audio_timeout_triggered":
                    pass
                else:
                    pass
        except Exception as e:
            logger.error(f"Breaking error processing events for session: {e}")
            raise e
