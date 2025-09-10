"""Base interfaces and abstract classes for real-time agents."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Protocol, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Types of messages in real-time communication."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"
    STATUS = "status"


class ConnectionStatus(Enum):
    """Connection status for real-time agents."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class Message:
    """Represents a message in the real-time conversation."""
    
    id: str
    type: MessageType
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


@dataclass
class AgentResponse:
    """Response from the real-time agent."""
    
    message: Message
    is_final: bool = True
    usage: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            "message": self.message.to_dict(),
            "is_final": self.is_final,
            "usage": self.usage
        }


class EventHandler(Protocol):
    """Protocol for handling real-time events."""
    
    async def on_message(self, message: Message) -> None:
        """Handle incoming message."""
        ...
    
    async def on_connection_status(self, status: ConnectionStatus) -> None:
        """Handle connection status changes."""
        ...
    
    async def on_error(self, error: Exception) -> None:
        """Handle errors."""
        ...


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider."""
        pass
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Message],
        stream: bool = True,
        **kwargs: Any
    ) -> Union[AgentResponse, AsyncIterator[AgentResponse]]:
        """Generate response from the AI provider."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the provider connection."""
        pass


class RealTimeSession(ABC):
    """Abstract base class for real-time sessions."""
    
    @abstractmethod
    async def start(self) -> None:
        """Start the real-time session."""
        pass
    
    @abstractmethod
    async def send_message(self, message: Message) -> None:
        """Send a message in the session."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the real-time session."""
        pass
    
    @property
    @abstractmethod
    def status(self) -> ConnectionStatus:
        """Get current connection status."""
        pass