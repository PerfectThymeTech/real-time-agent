"""Utility functions for real-time agents."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.interfaces import Message, MessageType


class LoggingEventHandler:
    """Simple event handler that logs all events."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize logging event handler.
        
        Args:
            logger: Optional logger instance. If not provided, creates a new one.
        """
        self.logger = logger or logging.getLogger(__name__)
    
    async def on_message(self, message: Message) -> None:
        """Log incoming messages."""
        self.logger.info(f"Message [{message.type.value}]: {message.content[:100]}...")
    
    async def on_connection_status(self, status) -> None:
        """Log connection status changes."""
        self.logger.info(f"Connection status changed to: {status.value}")
    
    async def on_error(self, error: Exception) -> None:
        """Log errors."""
        self.logger.error(f"Error occurred: {error}")


class ConversationExporter:
    """Utility for exporting conversation history."""
    
    @staticmethod
    def to_json(messages: List[Message], pretty: bool = True) -> str:
        """Export messages to JSON format.
        
        Args:
            messages: List of messages to export
            pretty: Whether to format JSON with indentation
            
        Returns:
            JSON string representation of the conversation
        """
        conversation_data = {
            "conversation": [message.to_dict() for message in messages],
            "exported_at": datetime.now().isoformat(),
            "message_count": len(messages)
        }
        
        if pretty:
            return json.dumps(conversation_data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(conversation_data, ensure_ascii=False)
    
    @staticmethod
    def to_markdown(messages: List[Message]) -> str:
        """Export messages to Markdown format.
        
        Args:
            messages: List of messages to export
            
        Returns:
            Markdown string representation of the conversation
        """
        markdown_lines = [
            "# Conversation Export",
            f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total messages: {len(messages)}",
            "",
            "---",
            ""
        ]
        
        for message in messages:
            timestamp = message.timestamp.strftime("%H:%M:%S")
            
            if message.type == MessageType.USER:
                markdown_lines.extend([
                    f"## User ({timestamp})",
                    message.content,
                    ""
                ])
            elif message.type == MessageType.ASSISTANT:
                markdown_lines.extend([
                    f"## Assistant ({timestamp})",
                    message.content,
                    ""
                ])
            elif message.type == MessageType.SYSTEM:
                markdown_lines.extend([
                    f"## System ({timestamp})",
                    f"_{message.content}_",
                    ""
                ])
        
        return "\n".join(markdown_lines)


class TokenCounter:
    """Utility for counting tokens in messages."""
    
    @staticmethod
    def estimate_tokens(text: str, model: str = "gpt-4") -> int:
        """Estimate token count for text.
        
        This is a rough estimation. For accurate counting, use tiktoken library.
        
        Args:
            text: Text to count tokens for
            model: Model name for token estimation
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for most models
        return len(text) // 4
    
    @staticmethod
    def estimate_conversation_tokens(messages: List[Message], model: str = "gpt-4") -> int:
        """Estimate total tokens for a conversation.
        
        Args:
            messages: List of messages in the conversation
            model: Model name for token estimation
            
        Returns:
            Estimated total token count
        """
        total_tokens = 0
        
        for message in messages:
            # Add tokens for the message content
            total_tokens += TokenCounter.estimate_tokens(message.content, model)
            
            # Add overhead tokens for message structure (role, etc.)
            total_tokens += 10  # Rough overhead per message
        
        return total_tokens


class MessageValidator:
    """Utility for validating messages."""
    
    @staticmethod
    def validate_message(message: Message) -> List[str]:
        """Validate a message and return list of validation errors.
        
        Args:
            message: Message to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not message.id:
            errors.append("Message ID is required")
        
        if not message.content:
            errors.append("Message content is required")
        
        if not message.timestamp:
            errors.append("Message timestamp is required")
        
        if message.type not in MessageType:
            errors.append(f"Invalid message type: {message.type}")
        
        return errors
    
    @staticmethod
    def validate_conversation(messages: List[Message]) -> List[str]:
        """Validate a conversation and return list of validation errors.
        
        Args:
            messages: List of messages to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        for i, message in enumerate(messages):
            message_errors = MessageValidator.validate_message(message)
            for error in message_errors:
                errors.append(f"Message {i}: {error}")
        
        return errors


class AsyncRetry:
    """Utility for retrying async operations."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            backoff_factor: Factor to multiply delay by for each retry
            exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions
    
    async def __call__(self, func, *args, **kwargs):
        """Execute function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        current_delay = self.delay
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:  # Not the last attempt
                    await asyncio.sleep(current_delay)
                    current_delay *= self.backoff_factor
                else:
                    break
        
        # If we get here, all retries failed
        raise last_exception