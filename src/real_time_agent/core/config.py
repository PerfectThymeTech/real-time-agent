"""Configuration management for real-time agents."""

import os
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for real-time agent."""
    
    # Provider configuration
    provider: Literal["azure_openai", "ai_foundry", "mock"] = Field(
        default="azure_openai",
        description="AI provider to use for the agent"
    )
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT"),
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY"),
        description="Azure OpenAI API key"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-01",
        description="Azure OpenAI API version"
    )
    azure_openai_deployment: Optional[str] = Field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        description="Azure OpenAI deployment name"
    )
    
    # AI Foundry Configuration
    ai_foundry_endpoint: Optional[str] = Field(
        default_factory=lambda: os.getenv("AI_FOUNDRY_ENDPOINT"),
        description="AI Foundry endpoint URL"
    )
    ai_foundry_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("AI_FOUNDRY_API_KEY"),
        description="AI Foundry API key"
    )
    
    # Agent behavior configuration
    max_tokens: int = Field(
        default=1000,
        description="Maximum tokens for response generation"
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature for response generation"
    )
    streaming: bool = Field(
        default=True,
        description="Enable streaming responses"
    )
    
    # Real-time configuration
    websocket_timeout: int = Field(
        default=30,
        description="WebSocket connection timeout in seconds"
    )
    heartbeat_interval: int = Field(
        default=10,
        description="Heartbeat interval in seconds"
    )
    max_reconnect_attempts: int = Field(
        default=5,
        description="Maximum reconnection attempts"
    )
    
    # System configuration
    system_prompt: str = Field(
        default="You are a helpful AI assistant providing real-time responses.",
        description="System prompt for the agent"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    class Config:
        env_prefix = "REAL_TIME_AGENT_"
        case_sensitive = False


class ProviderConfig(BaseModel):
    """Base configuration for AI providers."""
    
    endpoint: str = Field(..., description="Provider endpoint URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    class Config:
        extra = "allow"