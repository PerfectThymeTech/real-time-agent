"""
Real-Time Agent Reference Implementation

This package provides a reference design for building real-time agents
using Azure OpenAI or AI Foundry services.
"""

__version__ = "0.1.0"
__author__ = "Perfect Thyme Tech"

from .core.agent import RealTimeAgent
from .core.config import AgentConfig

# Import providers with error handling for optional dependencies
try:
    from .integrations.azure_openai import AzureOpenAIProvider
except ImportError:
    AzureOpenAIProvider = None

try:
    from .integrations.ai_foundry import AIFoundryProvider
except ImportError:
    AIFoundryProvider = None

__all__ = [
    "RealTimeAgent",
    "AgentConfig", 
]

# Only add providers to __all__ if they're available
if AzureOpenAIProvider:
    __all__.append("AzureOpenAIProvider")
if AIFoundryProvider:
    __all__.append("AIFoundryProvider")