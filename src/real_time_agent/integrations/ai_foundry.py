"""AI Foundry provider implementation for real-time agents."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import aiohttp
from azure.identity import DefaultAzureCredential
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage

from ..core.interfaces import AIProvider, AgentResponse, Message, MessageType
from ..core.config import AgentConfig


class AIFoundryProvider(AIProvider):
    """AI Foundry provider for real-time agent capabilities."""
    
    def __init__(self, config: AgentConfig):
        """Initialize AI Foundry provider.
        
        Args:
            config: Agent configuration containing AI Foundry settings
        """
        self.config = config
        self.client: Optional[ChatCompletionsClient] = None
        self.logger = logging.getLogger(__name__)
        
        # Validate required configuration
        if not config.ai_foundry_endpoint:
            raise ValueError("AI Foundry endpoint is required")
    
    async def initialize(self) -> None:
        """Initialize the AI Foundry client."""
        self.logger.info("Initializing AI Foundry provider")
        
        try:
            # Use API key if provided, otherwise use Azure credential
            if self.config.ai_foundry_api_key:
                from azure.core.credentials import AzureKeyCredential
                credential = AzureKeyCredential(self.config.ai_foundry_api_key)
            else:
                credential = DefaultAzureCredential()
            
            self.client = ChatCompletionsClient(
                endpoint=self.config.ai_foundry_endpoint,
                credential=credential
            )
            
            # Test the connection
            await self._test_connection()
            self.logger.info("AI Foundry provider initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Foundry provider: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """Test the AI Foundry connection."""
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        try:
            # Simple test call to verify connectivity
            response = await self.client.complete(
                messages=[UserMessage(content="Hello")],
                max_tokens=1,
                temperature=0
            )
            self.logger.debug("Connection test successful")
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            raise
    
    def _messages_to_foundry_format(self, messages: List[Message]) -> List[Any]:
        """Convert internal message format to AI Foundry format."""
        foundry_messages = []
        
        for message in messages:
            if message.type == MessageType.USER:
                foundry_messages.append(UserMessage(content=message.content))
            elif message.type == MessageType.ASSISTANT:
                foundry_messages.append(AssistantMessage(content=message.content))
            elif message.type == MessageType.SYSTEM:
                foundry_messages.append(SystemMessage(content=message.content))
        
        return foundry_messages
    
    async def generate_response(
        self,
        messages: List[Message],
        stream: bool = True,
        **kwargs: Any
    ) -> Union[AgentResponse, AsyncIterator[AgentResponse]]:
        """Generate response using AI Foundry.
        
        Args:
            messages: List of conversation messages
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API call
            
        Returns:
            Single response or async iterator for streaming responses
        """
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Convert messages to AI Foundry format
        foundry_messages = self._messages_to_foundry_format(messages)
        
        # Prepare API call parameters
        api_params = {
            "messages": foundry_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": stream
        }
        
        # Add additional parameters
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature"] and value is not None:
                api_params[key] = value
        
        try:
            if stream:
                return self._generate_streaming_response(api_params)
            else:
                return await self._generate_single_response(api_params)
                
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            raise
    
    async def _generate_single_response(self, api_params: Dict[str, Any]) -> AgentResponse:
        """Generate a single (non-streaming) response."""
        response = await self.client.complete(**api_params)
        
        # Extract response content
        content = response.choices[0].message.content or ""
        
        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.ASSISTANT,
            content=content,
            timestamp=datetime.now(),
            metadata={
                "model": getattr(response, 'model', 'ai-foundry'),
                "finish_reason": response.choices[0].finish_reason
            }
        )
        
        # Create usage info
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return AgentResponse(
            message=message,
            is_final=True,
            usage=usage
        )
    
    async def _generate_streaming_response(
        self, 
        api_params: Dict[str, Any]
    ) -> AsyncIterator[AgentResponse]:
        """Generate streaming responses."""
        message_id = str(uuid.uuid4())
        accumulated_content = ""
        
        async for chunk in await self.client.complete(**api_params):
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content_delta = chunk.choices[0].delta.content
                accumulated_content += content_delta
                
                # Create incremental message
                message = Message(
                    id=message_id,
                    type=MessageType.ASSISTANT,
                    content=content_delta,
                    timestamp=datetime.now(),
                    metadata={
                        "model": getattr(chunk, 'model', 'ai-foundry'),
                        "accumulated_content": accumulated_content
                    }
                )
                
                # Check if this is the final chunk
                is_final = (
                    chunk.choices[0].finish_reason is not None and
                    chunk.choices[0].finish_reason != "null"
                )
                
                yield AgentResponse(
                    message=message,
                    is_final=is_final,
                    usage=None  # Usage info typically comes with final chunk
                )
    
    async def close(self) -> None:
        """Close the AI Foundry provider."""
        self.logger.info("Closing AI Foundry provider")
        
        if self.client:
            await self.client.close()
            self.client = None