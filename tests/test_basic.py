"""Basic tests for the real-time agent implementation."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from real_time_agent.core.config import AgentConfig
from real_time_agent.core.interfaces import Message, MessageType, ConnectionStatus
from real_time_agent.core.agent import RealTimeAgent
from real_time_agent.utils.helpers import (
    LoggingEventHandler, 
    ConversationExporter,
    TokenCounter,
    MessageValidator
)


class TestAgentConfig:
    """Test agent configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AgentConfig()
        assert config.provider == "azure_openai"
        assert config.max_tokens == 1000
        assert config.temperature == 0.7
        assert config.streaming is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = AgentConfig(
            provider="ai_foundry",
            max_tokens=500,
            temperature=0.5,
            streaming=False
        )
        assert config.provider == "ai_foundry"
        assert config.max_tokens == 500
        assert config.temperature == 0.5
        assert config.streaming is False


class TestMessage:
    """Test message functionality."""
    
    def test_message_creation(self):
        """Test message creation and conversion."""
        message = Message(
            id="test-123",
            type=MessageType.USER,
            content="Hello, world!",
            timestamp=datetime.now(),
            metadata={"test": "value"}
        )
        
        assert message.id == "test-123"
        assert message.type == MessageType.USER
        assert message.content == "Hello, world!"
        assert message.metadata["test"] == "value"
    
    def test_message_to_dict(self):
        """Test message serialization."""
        message = Message(
            id="test-123",
            type=MessageType.USER,
            content="Hello, world!",
            timestamp=datetime.now()
        )
        
        message_dict = message.to_dict()
        assert message_dict["id"] == "test-123"
        assert message_dict["type"] == "user"
        assert message_dict["content"] == "Hello, world!"
        assert "timestamp" in message_dict


class TestUtilities:
    """Test utility functions."""
    
    def test_token_counter(self):
        """Test token counting utility."""
        text = "Hello, world! This is a test message."
        tokens = TokenCounter.estimate_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_conversation_tokens(self):
        """Test conversation token counting."""
        messages = [
            Message(
                id="1", 
                type=MessageType.USER, 
                content="Hello", 
                timestamp=datetime.now()
            ),
            Message(
                id="2", 
                type=MessageType.ASSISTANT, 
                content="Hi there!", 
                timestamp=datetime.now()
            )
        ]
        
        total_tokens = TokenCounter.estimate_conversation_tokens(messages)
        assert total_tokens > 0
        assert isinstance(total_tokens, int)
    
    def test_message_validator(self):
        """Test message validation."""
        # Valid message
        valid_message = Message(
            id="test-123",
            type=MessageType.USER,
            content="Hello",
            timestamp=datetime.now()
        )
        errors = MessageValidator.validate_message(valid_message)
        assert len(errors) == 0
        
        # Invalid message
        invalid_message = Message(
            id="",
            type=MessageType.USER,
            content="",
            timestamp=datetime.now()
        )
        errors = MessageValidator.validate_message(invalid_message)
        assert len(errors) > 0
    
    def test_conversation_exporter(self):
        """Test conversation export functionality."""
        messages = [
            Message(
                id="1", 
                type=MessageType.USER, 
                content="Hello", 
                timestamp=datetime.now()
            ),
            Message(
                id="2", 
                type=MessageType.ASSISTANT, 
                content="Hi there!", 
                timestamp=datetime.now()
            )
        ]
        
        # Test JSON export
        json_export = ConversationExporter.to_json(messages)
        assert "conversation" in json_export
        assert "exported_at" in json_export
        
        # Test Markdown export
        markdown_export = ConversationExporter.to_markdown(messages)
        assert "# Conversation Export" in markdown_export
        assert "## User" in markdown_export
        assert "## Assistant" in markdown_export


class TestEventHandler:
    """Test event handler functionality."""
    
    @pytest.mark.asyncio
    async def test_logging_event_handler(self):
        """Test logging event handler."""
        handler = LoggingEventHandler()
        
        message = Message(
            id="test-123",
            type=MessageType.USER,
            content="Test message",
            timestamp=datetime.now()
        )
        
        # Should not raise any exceptions
        await handler.on_message(message)
        await handler.on_connection_status(ConnectionStatus.CONNECTED)
        await handler.on_error(Exception("Test error"))


class MockProvider:
    """Mock AI provider for testing."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Mock initialization."""
        self.initialized = True
    
    async def generate_response(self, messages, stream=True, **kwargs):
        """Mock response generation."""
        from real_time_agent.core.interfaces import AgentResponse
        
        response_message = Message(
            id="response-123",
            type=MessageType.ASSISTANT,
            content="Mock response",
            timestamp=datetime.now()
        )
        
        return AgentResponse(
            message=response_message,
            is_final=True,
            usage={"total_tokens": 10}
        )
    
    async def close(self):
        """Mock close."""
        self.initialized = False


class TestRealTimeAgent:
    """Test real-time agent functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization."""
        config = AgentConfig()
        provider = MockProvider()
        agent = RealTimeAgent(config, provider)
        
        await agent.initialize()
        assert agent.status == ConnectionStatus.CONNECTED
        assert provider.initialized is True
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending messages."""
        config = AgentConfig(streaming=False)
        provider = MockProvider()
        agent = RealTimeAgent(config, provider)
        
        await agent.initialize()
        
        response = await agent.send_message("Hello, agent!")
        assert response.message.content == "Mock response"
        assert response.is_final is True
        
        # Check conversation history
        history = await agent.get_conversation_history()
        assert len(history) == 2  # User message + Assistant response
        assert history[0].type == MessageType.USER
        assert history[1].type == MessageType.ASSISTANT
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_system_prompt(self):
        """Test system prompt functionality."""
        config = AgentConfig()
        provider = MockProvider()
        agent = RealTimeAgent(config, provider)
        
        await agent.initialize()
        
        await agent.set_system_prompt("You are a test assistant.")
        
        history = await agent.get_conversation_history()
        assert len(history) == 1
        assert history[0].type == MessageType.SYSTEM
        assert history[0].content == "You are a test assistant."
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_clear_conversation(self):
        """Test clearing conversation history."""
        config = AgentConfig(streaming=False)
        provider = MockProvider()
        agent = RealTimeAgent(config, provider)
        
        await agent.initialize()
        
        # Send a message
        await agent.send_message("Hello!")
        
        # Check history has messages
        history = await agent.get_conversation_history()
        assert len(history) > 0
        
        # Clear conversation
        await agent.clear_conversation()
        
        # Check history is empty
        history = await agent.get_conversation_history()
        assert len(history) == 0
        
        await agent.close()


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    import sys
    
    print("Running basic tests...")
    
    # Test configuration
    try:
        test_config = TestAgentConfig()
        test_config.test_default_config()
        test_config.test_custom_config()
        print("✅ Configuration tests passed")
    except Exception as e:
        print(f"❌ Configuration tests failed: {e}")
        sys.exit(1)
    
    # Test message functionality
    try:
        test_message = TestMessage()
        test_message.test_message_creation()
        test_message.test_message_to_dict()
        print("✅ Message tests passed")
    except Exception as e:
        print(f"❌ Message tests failed: {e}")
        sys.exit(1)
    
    # Test utilities
    try:
        test_utils = TestUtilities()
        test_utils.test_token_counter()
        test_utils.test_conversation_tokens()
        test_utils.test_message_validator()
        test_utils.test_conversation_exporter()
        print("✅ Utility tests passed")
    except Exception as e:
        print(f"❌ Utility tests failed: {e}")
        sys.exit(1)
    
    print("✅ All basic tests passed!")
    print("Note: Run 'pytest tests/' for full async test suite")