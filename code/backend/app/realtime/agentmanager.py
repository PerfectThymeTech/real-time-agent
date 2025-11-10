import asyncio
import os
from pathlib import Path
from collections import defaultdict
from agents.realtime import RealtimeAgent, RealtimeRunner, realtime_handoff
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
from app.logs import setup_logging
from app.models.realtime import AgentConfig, HandoffConfig

logger = setup_logging(__name__)


class AgentManager:
    def __init__(self, agent_directory: str):
        """
        Docstring for __init__
        
        :param self: Description
        :param agent_directory: Description
        :type agent_directory: str
        """
        # Dictionary to hold agents by their IDs
        self.agents = defaultdict(RealtimeAgent)
        self.opener_agent = None
        self.agent_handoffs = defaultdict(list[HandoffConfig])

        # Initialize by loading agents from the specified directory
        self.__load_agents(agent_directory=agent_directory)

        # Initialize handoffs
        self.__set_handoffs()

        # Define session properties
        self.session = None
        self.session_context = None
        self.receive_task = None

    def __load_agents(self, agent_directory: str) -> None:
        """
        Load agents from agent directory.

        :param self: Description
        :param agent_directory: Specifies the directory containing agent configuration files.
        :type agent_directory: str
        :return: None
        :rtype: None
        """
        for agent_file in os.listdir(path=agent_directory):
            # Check if agent_file is an actual file
            if not os.path.isfile(agent_file):
                logger.warning(f"Failed to load agent. Agent file '{agent_file}' is not a file.")
                continue

            # Check if agent_file is a yaml file
            if not Path(agent_file).suffix in ["yaml", "yml"]:
                logger.warning(f"Failed to load agent. Agent file '{agent_file}' is not in yaml format.")
                continue

            # Load the agent config from the yaml file
            try:
                with open(agent_file, "r") as f:
                    yaml_content = f.read()
                    agent_config = AgentConfig(**yaml_content)
            except Exception as e:
                logger.error(f"Failed to load agent from file '{agent_file}': {e}")
                continue

            # TODO: Add support for tools, mcp_servers, output_guardrails
            # Create the RealtimeAgent instance
            agent = RealtimeAgent(
                name=agent_config.name,
                instructions=agent_config.instructions,
            )
            self.agents[agent_config.name] = agent

            # If agent is marked as opener, set it as the opener agent
            if agent_config.opener:
                self.opener_agent = agent

            # Define agent handoffs
            self.agent_handoffs[agent_config.name] = agent_config.handoffs
    
    def __set_handoffs(self) -> None:
        """
        Set handoffs between agents.

        :param self: Description
        :return: None
        :rtype: None
        """
        for agent_name, handoff_configs in self.agent_handoffs.items():
            agent: RealtimeAgent = self.agents.get(agent_name)

            # Check if agent can be loaded
            if not agent:
                logger.warning(f"Failed to load agent. Agent '{agent_name}' not found for handoff setup.")
                continue
            
            # Load agent handoff configurations
            for handoff_config in handoff_configs:
                # Load agent to which we want to handover
                handoff_agent = self.agents.get(handoff_config.agent_name)
                handoff_condition = handoff_config.condition

                # Check if 
                if not handoff_agent or not handoff_condition:
                    logger.warning(f"Handoff agent '{handoff_config.agent_name}' or condition '{handoff_config.condition}' not found for agent '{agent_name}'.")
                    continue

                agent.handoffs.append(
                    realtime_handoff(
                        agent=handoff_agent,
                        tool_description=handoff_condition,
                        is_enabled=True,
                    )
                )

    async def init_realtime_session(self, azure_open_ai_endpoint: str, azure_open_ai_key: str, realtime_model_name: str, transcription_model_name: str) -> None:
        """
        Initialize the real time session.

        :param self: Description
        :return: The opener agent for the session.
        :rtype: RealtimeAgent
        """
        # Create the real time runner
        real_time_runner = RealtimeRunner(
            starting_agent=self.opener_agent,
            config=RealtimeRunConfig(
                model_settings=RealtimeSessionModelSettings(
                    model_name=realtime_model_name,
                    input_audio_format="pcm16",
                    input_audio_transcription=RealtimeInputAudioTranscriptionConfig(
                        language="en",
                        model=transcription_model_name,
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
            api_key=azure_open_ai_key,
            url=f"wss://{azure_open_ai_endpoint.removeprefix('https://')}openai/v1/realtime?model={realtime_model_name}",
        )

        # Create real time session
        logger.info(
            f"Initialize model real time session with endpoint '{azure_open_ai_endpoint}' and model '{realtime_model_name}'"
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
        pass

    async def process_realtime_messages(self) -> None:
        pass

    async def send_audio(self, audio: bytes):
        """
        Send audio data to the real time model session.
        """
        await self.session.send_audio(
            audio=audio,
            commit=False,
        )
