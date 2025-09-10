"""Azure OpenAI provider implementation for real-time agents."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential

from ..core.interfaces import AIProvider, AgentResponse, Message, MessageType
from ..core.config import AgentConfig


class AzureOpenAIProvider(AIProvider):
    """Azure OpenAI provider for real-time agent capabilities."""
    
    def __init__(self, config: AgentConfig):
        """Initialize Azure OpenAI provider.
        
        Args:
            config: Agent configuration containing Azure OpenAI settings
        """
        self.config = config
        self.client: Optional[AsyncAzureOpenAI] = None
        self.logger = logging.getLogger(__name__)
        
        # Validate required configuration
        if not config.azure_openai_endpoint:
            raise ValueError("Azure OpenAI endpoint is required")
        if not config.azure_openai_deployment:
            raise ValueError("Azure OpenAI deployment name is required")
    
    async def initialize(self) -> None:
        """Initialize the Azure OpenAI client."""
        self.logger.info("Initializing Azure OpenAI provider")
        
        try:
            # Use API key if provided, otherwise use Azure credential
            if self.config.azure_openai_api_key:
                self.client = AsyncAzureOpenAI(
                    api_key=self.config.azure_openai_api_key,
                    api_version=self.config.azure_openai_api_version,
                    azure_endpoint=self.config.azure_openai_endpoint
                )
            else:
                # Use managed identity or default Azure credential
                credential = DefaultAzureCredential()
                token = await credential.get_token("https://cognitiveservices.azure.com/.default")
                
                self.client = AsyncAzureOpenAI(
                    api_key=token.token,
                    api_version=self.config.azure_openai_api_version,
                    azure_endpoint=self.config.azure_openai_endpoint
                )
            
            # Test the connection
            await self._test_connection()
            self.logger.info("Azure OpenAI provider initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure OpenAI provider: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """Test the Azure OpenAI connection."""
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        try:
            # Simple test call to verify connectivity
            response = await self.client.chat.completions.create(
                model=self.config.azure_openai_deployment,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,
                temperature=0
            )
            self.logger.debug("Connection test successful")
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            raise
    
    def _messages_to_openai_format(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Convert internal message format to OpenAI format."""
        openai_messages = []
        
        for message in messages:
            role_map = {
                MessageType.USER: "user",
                MessageType.ASSISTANT: "assistant",
                MessageType.SYSTEM: "system"
            }
            
            if message.type in role_map:
                openai_messages.append({
                    "role": role_map[message.type],
                    "content": message.content
                })
        
        return openai_messages
    
    async def generate_response(
        self,
        messages: List[Message],
        stream: bool = True,
        **kwargs: Any
    ) -> Union[AgentResponse, AsyncIterator[AgentResponse]]:
        """Generate response using Azure OpenAI.
        
        Args:
            messages: List of conversation messages
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API call
            
        Returns:
            Single response or async iterator for streaming responses
        """
        if not self.client:
            raise RuntimeError("Provider not initialized")
        
        # Convert messages to OpenAI format
        openai_messages = self._messages_to_openai_format(messages)
        
        # Prepare API call parameters
        api_params = {
            "model": self.config.azure_openai_deployment,
            "messages": openai_messages,
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
        response = await self.client.chat.completions.create(**api_params)
        
        # Extract response content
        content = response.choices[0].message.content or ""
        
        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.ASSISTANT,
            content=content,
            timestamp=datetime.now(),
            metadata={
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        )
        
        # Create usage info
        usage = None
        if response.usage:
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
        
        async for chunk in await self.client.chat.completions.create(**api_params):
            if chunk.choices and chunk.choices[0].delta.content:
                content_delta = chunk.choices[0].delta.content
                accumulated_content += content_delta
                
                # Create incremental message
                message = Message(
                    id=message_id,
                    type=MessageType.ASSISTANT,
                    content=content_delta,
                    timestamp=datetime.now(),
                    metadata={
                        "model": chunk.model,
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
        """Close the Azure OpenAI provider."""
        self.logger.info("Closing Azure OpenAI provider")
        
        if self.client:
            await self.client.close()
            self.client = None