# Real-Time Agent Reference Implementation

A comprehensive reference design and Python implementation for building real-time AI agents using Azure OpenAI or AI Foundry. This repository provides architecture patterns, best practices, and production-ready code for implementing conversational AI agents with real-time streaming capabilities.

## 🎯 Overview

This project demonstrates how to build scalable, real-time AI agents that can:
- Handle streaming responses for immediate user feedback
- Support multiple AI providers (Azure OpenAI and AI Foundry)
- Implement robust error handling and reconnection logic
- Provide comprehensive event handling and logging
- Scale for production use cases

## ✨ Features

- **Multi-Provider Support**: Seamlessly switch between Azure OpenAI and AI Foundry
- **Real-Time Streaming**: Get immediate response chunks as they're generated
- **Event-Driven Architecture**: Comprehensive event handling for messages, connections, and errors
- **Configuration Management**: Flexible configuration via environment variables or code
- **Production Ready**: Includes logging, error handling, retry logic, and validation
- **Extensible Design**: Easy to extend with new providers or custom functionality
- **Type Safety**: Full type annotations for better development experience

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/PerfectThymeTech/real-time-agent.git
cd real-time-agent

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Configuration

1. Copy the configuration template:
   ```bash
   cp config/.env.template .env
   ```

2. Update the `.env` file with your credentials:
   ```env
   # For Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   
   # For AI Foundry
   AI_FOUNDRY_ENDPOINT=https://your-foundry-endpoint.com/
   AI_FOUNDRY_API_KEY=your-foundry-api-key-here
   ```

### Basic Usage

```python
import asyncio
from real_time_agent import RealTimeAgent, AgentConfig, AzureOpenAIProvider

async def main():
    # Create configuration
    config = AgentConfig(
        provider="azure_openai",
        azure_openai_endpoint="https://your-resource.openai.azure.com/",
        azure_openai_deployment="gpt-4",
        streaming=True
    )
    
    # Create provider and agent
    provider = AzureOpenAIProvider(config)
    agent = RealTimeAgent(config, provider)
    
    # Initialize and use
    await agent.initialize()
    
    # Send a message and get streaming response
    async for response in await agent.send_message("Hello, how can you help me?"):
        print(response.message.content, end='', flush=True)
        if response.is_final:
            break
    
    await agent.close()

asyncio.run(main())
```

## 📖 Documentation

### Architecture Overview

The real-time agent system follows a modular, event-driven architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │───▶│  RealTimeAgent   │───▶│   AI Provider   │
│     Layer       │    │                  │    │ (Azure/Foundry) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │  Event Handler  │
                       │   (Optional)    │
                       └─────────────────┘
```

### Key Components

1. **RealTimeAgent**: Main orchestrator handling conversation flow
2. **AI Providers**: Pluggable providers for different AI services
3. **Configuration**: Centralized configuration management
4. **Event Handlers**: Optional callbacks for real-time events
5. **Utilities**: Helper functions for common tasks

### Provider Comparison

| Feature | Azure OpenAI | AI Foundry |
|---------|--------------|------------|
| Streaming | ✅ | ✅ |
| Authentication | API Key / Managed Identity | API Key / Managed Identity |
| Model Selection | Deployment-based | Model-based |
| Enterprise Features | ✅ | ✅ |
| Cost | Pay-per-token | Varies |

## 📁 Project Structure

```
src/real_time_agent/
├── core/
│   ├── agent.py          # Main agent implementation
│   ├── config.py         # Configuration management
│   └── interfaces.py     # Abstract base classes
├── integrations/
│   ├── azure_openai.py   # Azure OpenAI provider
│   └── ai_foundry.py     # AI Foundry provider
├── utils/
│   └── helpers.py        # Utility functions
└── examples/
    ├── basic_usage.py    # Basic example
    ├── advanced_streaming.py # Advanced streaming example
    └── ai_foundry_example.py # AI Foundry example
```

## 🔧 Configuration Options

### Environment Variables

All configuration can be set via environment variables with the `REAL_TIME_AGENT_` prefix:

- `REAL_TIME_AGENT_PROVIDER`: AI provider to use (`azure_openai` or `ai_foundry`)
- `REAL_TIME_AGENT_MAX_TOKENS`: Maximum tokens per response
- `REAL_TIME_AGENT_TEMPERATURE`: Response randomness (0.0-1.0)
- `REAL_TIME_AGENT_STREAMING`: Enable streaming responses
- `REAL_TIME_AGENT_LOG_LEVEL`: Logging level

### Programmatic Configuration

```python
config = AgentConfig(
    provider="azure_openai",
    max_tokens=1000,
    temperature=0.7,
    streaming=True,
    system_prompt="Your custom system prompt",
    # Azure OpenAI specific
    azure_openai_endpoint="https://your-resource.openai.azure.com/",
    azure_openai_deployment="gpt-4",
    # AI Foundry specific  
    ai_foundry_endpoint="https://your-foundry-endpoint.com/"
)
```

## 🎛️ Advanced Usage

### Custom Event Handling

```python
from real_time_agent.core.interfaces import EventHandler

class CustomEventHandler:
    async def on_message(self, message):
        # Custom message handling logic
        print(f"Received: {message.content}")
    
    async def on_connection_status(self, status):
        # Handle connection changes
        print(f"Status: {status}")
    
    async def on_error(self, error):
        # Custom error handling
        print(f"Error: {error}")

# Use with agent
handler = CustomEventHandler()
agent = RealTimeAgent(config, provider, handler)
```

### Conversation Management

```python
# Get conversation history
history = await agent.get_conversation_history()

# Clear conversation
await agent.clear_conversation()

# Update system prompt
await agent.set_system_prompt("New system prompt")

# Export conversation
from real_time_agent.utils.helpers import ConversationExporter
json_export = ConversationExporter.to_json(history)
markdown_export = ConversationExporter.to_markdown(history)
```

## 🧪 Examples

Run the included examples to see the agent in action:

```bash
# Basic usage example
python src/real_time_agent/examples/basic_usage.py

# Advanced streaming with event handling
python src/real_time_agent/examples/advanced_streaming.py

# AI Foundry integration
python src/real_time_agent/examples/ai_foundry_example.py
```

## 🔐 Security Best Practices

1. **Use Environment Variables**: Store API keys in environment variables, not code
2. **Managed Identity**: Use Azure Managed Identity in production when possible
3. **Rate Limiting**: Implement rate limiting for user-facing applications
4. **Input Validation**: Validate and sanitize user inputs
5. **Logging**: Be careful not to log sensitive information

## 🤝 Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an [issue](https://github.com/PerfectThymeTech/real-time-agent/issues) for bug reports or feature requests
- Check the [documentation](docs/) for detailed guides
- Review the [examples](src/real_time_agent/examples/) for implementation patterns

## 🎯 Use Cases

This reference implementation is ideal for:
- Customer service chatbots
- Technical support agents
- Educational AI tutors
- Content generation tools
- Interactive AI assistants
- Real-time translation services

---

Built with ❤️ by Perfect Thyme Tech
