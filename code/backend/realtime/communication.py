import asyncio
import json
import base64
from agents.realtime import RealtimeAgent, RealtimeRunner
from agents.realtime.events import RealtimeAudioEnd
from agents.realtime.model import RealtimeModelConfig
from agents.realtime.model_inputs import RealtimeModelSendRawMessage
from agents.realtime.model_events import RealtimeModelRawServerEvent, RealtimeModelInputAudioTranscriptionCompletedEvent
from agents.realtime.session import RealtimeSession
from agents.realtime.config import RealtimeRunConfig, RealtimeSessionModelSettings, RealtimeInputAudioTranscriptionConfig, RealtimeModelTracingConfig, RealtimeTurnDetectionConfig
from agents.mcp import MCPServerStreamableHttp
from utils import setup_logging, _truncate_str
from fastapi import WebSocket
from core.settings import settings
from numpy import ndarray


logger = setup_logging(__name__)


class CommunicationHandler:
    async def __init__(self, websocket: WebSocket):
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
            )
        )

        # Create real time model config
        real_time_model_config = RealtimeModelConfig(
            api_key=settings.AZURE_OPENAI_API_KEY,
            url=f"wss://{settings.AZURE_OPENAI_ENDPOINT}openai/v1/realtime?model={settings.REALTIME_MODEL_NAME}",    
        )

        # Create real time session
        logger.info(f"Initialize model real time session with endpoint '{settings.AZURE_OPENAI_ENDPOINT}' and model '{settings.REALTIME_MODEL_NAME}'")
        session_context = await real_time_runner.run(
            context=None,
            model_config=real_time_model_config,
        )
        session = await session_context.__aenter__()

        # Start handling real time messages
        receive_task = asyncio.create_task(handle_realtime_messages(session=session, websocket=self.websocket))
        
        # Set properties
        self.session = session
        self.receive_task = receive_task
    
    async def recive_audio(self):
        """
        Receive audio data over the WebSocket from the client and send it to the real time model session.
        """
        while True:
            # Receive audio data from the WebSocket
            websocket_data = await self.websocket.receive_text()

            # Parse websocket data
            data = json.loads(websocket_data)
            data_type = data.get("type", None)

            match data_type:
                case "AudioData":
                    logger.info("Received audio data over WebSocket")

                    # Extract audio data
                    audio_data_b64 = data.get("data", None)

                    # Send audio data to the real time model session
                    if audio_data_b64:
                        await self.session.send_audio(
                            audio=audio_data_b64,
                            commit=False,
                        )
                
                case _:
                    logger.warning(f"Unknown data type received over WebSocket: {data_type}")



async def handle_realtime_messages(session: RealtimeSession, websocket: WebSocket):
    """
    Function that handles the messages from the Realtime service. TODO: Make function of CommunicationHandler class.

    This function only handles the non-audio messages.
    Audio is done through the callback so that it is faster and smoother.
    """
    async def return_audio(audio: bytes):
        logger.debug("Audio received from the model, sending to ACS client")
        await websocket.send_text(
            json.dumps(
                {
                    "kind": "AudioData",
                    "audioData": {
                        "data": audio # base64.b64encode(audio).decode("utf-8") # TODO: Validate this
                    },
                }
            )
        )

    try:
        logger.info("Handling realtime messages")
        async for event in session:
            logger.info(f"Event received: {event.type}")
            try:
                if event.data:
                    truncated_data = _truncate_str(str(event.data), 200)
                    logger.info(f"Data: '{truncated_data}'")
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
                pass
            elif event.type == "tool_end":
                pass
            elif event.type == "audio":
                if event.audio and event.audio.data:
                    await return_audio(event.audio.data)
                    pass
            elif event.type == "audio_interrupted":
                # await interrupt_audio()
                pass
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
                if event.data and isinstance(event.data, RealtimeModelRawServerEvent):
                    # Get raw event type
                    raw_event_type = event.data.data.get('type', None)
                    logger.info(f"Raw event type: {raw_event_type}")

                    if raw_event_type and raw_event_type == "response.output_audio_transcript.done":
                        logger.info(f"Model output transcription completed: '{event.data.data.get('transcript', None)}'")
                    elif raw_event_type and raw_event_type == "conversation.item.input_audio_transcription.completed":
                        logger.info(f"User input transcription completed: {event.data.data.get('transcript', None)}")

            elif event.type == "error":
                pass
            elif event.type == "input_audio_timeout_triggered":
                pass
            else:
                pass
    except Exception as e:
        logger.error(f"Breaking Error processing events for session: {e}")
        raise e
