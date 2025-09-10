"""Main real-time agent implementation."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .config import AgentConfig
from .interfaces import (
    AIProvider,
    AgentResponse,
    ConnectionStatus,
    EventHandler,
    Message,
    MessageType,
    RealTimeSession,
)


class RealTimeAgent:
    """Main real-time agent implementation."""
    
    def __init__(
        self,
        config: AgentConfig,
        provider: AIProvider,
        event_handler: Optional[EventHandler] = None
    ):
        """Initialize the real-time agent.
        
        Args:
            config: Agent configuration
            provider: AI provider instance
            event_handler: Optional event handler for callbacks
        """
        self.config = config
        self.provider = provider
        self.event_handler = event_handler
        self.session: Optional[RealTimeSession] = None
        self.conversation_history: List[Message] = []
        self._status = ConnectionStatus.DISCONNECTED
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, config.log_level.upper()))
        self.logger = logging.getLogger(__name__)
    
    @property
    def status(self) -> ConnectionStatus:
        """Get current connection status."""
        return self._status
    
    async def initialize(self) -> None:
        """Initialize the agent and provider."""
        self.logger.info("Initializing real-time agent")
        try:
            await self.provider.initialize()
            self._status = ConnectionStatus.CONNECTED
            self.logger.info("Agent initialization completed")
            
            if self.event_handler:
                await self.event_handler.on_connection_status(self._status)
                
        except Exception as e:
            self._status = ConnectionStatus.ERROR
            self.logger.error(f"Failed to initialize agent: {e}")
            
            if self.event_handler:
                await self.event_handler.on_error(e)
            raise
    
    async def send_message(
        self,
        content: str,
        message_type: MessageType = MessageType.USER,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Union[AgentResponse, AsyncIterator[AgentResponse]]:
        """Send a message and get response from the agent.
        
        Args:
            content: Message content
            message_type: Type of message
            metadata: Optional metadata
            
        Returns:
            Agent response or async iterator of responses for streaming
        """
        if self._status != ConnectionStatus.CONNECTED:
            raise RuntimeError("Agent is not connected")
        
        # Create user message
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        # Add to conversation history
        self.conversation_history.append(message)
        
        # Notify event handler
        if self.event_handler:
            await self.event_handler.on_message(message)
        
        try:
            # Get response from provider
            response = await self.provider.generate_response(
                messages=self.conversation_history,
                stream=self.config.streaming,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Handle streaming vs non-streaming responses
            if self.config.streaming:
                # Return the async generator directly for streaming
                return self._handle_streaming_response(response)
            else:
                # Handle single response
                return await self._handle_single_response(response)
                
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            
            if self.event_handler:
                await self.event_handler.on_error(e)
            raise
    
    async def _handle_streaming_response(
        self, 
        response_stream: AsyncIterator[AgentResponse]
    ) -> AsyncIterator[AgentResponse]:
        """Handle streaming responses from the provider."""
        accumulated_content = ""
        message_id = str(uuid.uuid4())
        
        async for chunk in response_stream:
            accumulated_content += chunk.message.content
            
            # Update message with accumulated content
            chunk.message.id = message_id
            chunk.message.timestamp = datetime.now()
            
            # Notify event handler
            if self.event_handler:
                await self.event_handler.on_message(chunk.message)
            
            yield chunk
            
            # If this is the final chunk, add to conversation history
            if chunk.is_final:
                final_message = Message(
                    id=message_id,
                    type=MessageType.ASSISTANT,
                    content=accumulated_content,
                    timestamp=datetime.now(),
                    metadata=chunk.message.metadata
                )
                self.conversation_history.append(final_message)
    
    async def _handle_single_response(self, response: AgentResponse) -> AgentResponse:
        """Handle single (non-streaming) responses from the provider."""
        # Add response to conversation history
        self.conversation_history.append(response.message)
        
        # Notify event handler
        if self.event_handler:
            await self.event_handler.on_message(response.message)
        
        return response
    
    async def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.logger.info("Clearing conversation history")
        self.conversation_history.clear()
    
    async def get_conversation_history(self) -> List[Message]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    async def set_system_prompt(self, prompt: str) -> None:
        """Set or update the system prompt."""
        self.config.system_prompt = prompt
        
        # Add system message to conversation if not already present
        if not self.conversation_history or self.conversation_history[0].type != MessageType.SYSTEM:
            system_message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.SYSTEM,
                content=prompt,
                timestamp=datetime.now()
            )
            self.conversation_history.insert(0, system_message)
        else:
            # Update existing system message
            self.conversation_history[0].content = prompt
            self.conversation_history[0].timestamp = datetime.now()
    
    async def close(self) -> None:
        """Close the agent and cleanup resources."""
        self.logger.info("Closing real-time agent")
        
        try:
            if self.provider:
                await self.provider.close()
            
            if self.session:
                await self.session.stop()
            
            self._status = ConnectionStatus.DISCONNECTED
            
            if self.event_handler:
                await self.event_handler.on_connection_status(self._status)
                
        except Exception as e:
            self.logger.error(f"Error during agent closure: {e}")
            raise