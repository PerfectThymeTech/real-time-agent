"""
Complete workflow example showing all features of the real-time agent.

This example demonstrates:
- Configuration management
- Provider initialization
- Real-time streaming
- Event handling
- Conversation management
- Error handling
- Export functionality
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import List

# Set Python path for direct execution
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from real_time_agent.core.config import AgentConfig
from real_time_agent.core.interfaces import Message, MessageType, ConnectionStatus
from real_time_agent.core.agent import RealTimeAgent
from real_time_agent.utils.helpers import LoggingEventHandler, ConversationExporter


class DemoEventHandler:
    """Demo event handler that shows all capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger("DemoHandler")
        self.message_count = 0
        self.token_usage = 0
        
    async def on_message(self, message: Message) -> None:
        """Handle messages with rich formatting."""
        self.message_count += 1
        
        if message.type == MessageType.USER:
            print(f"\n🙋 User [{self.message_count}]: {message.content}")
        elif message.type == MessageType.ASSISTANT:
            # Check if this is a streaming chunk or complete message
            if message.metadata and 'accumulated_content' in message.metadata:
                # This is streaming - show progress
                accumulated = message.metadata['accumulated_content']
                print(f"\r🤖 Assistant: {accumulated}", end='', flush=True)
            else:
                # Complete message
                print(f"\n🤖 Assistant [{self.message_count}]: {message.content}")
        elif message.type == MessageType.SYSTEM:
            print(f"\n⚙️  System [{self.message_count}]: {message.content}")
    
    async def on_connection_status(self, status: ConnectionStatus) -> None:
        """Handle connection status with visual indicators."""
        status_icons = {
            ConnectionStatus.CONNECTING: "🟡",
            ConnectionStatus.CONNECTED: "🟢", 
            ConnectionStatus.DISCONNECTED: "🔴",
            ConnectionStatus.ERROR: "❌",
            ConnectionStatus.RECONNECTING: "🔄"
        }
        
        icon = status_icons.get(status, "❓")
        print(f"\n{icon} Connection Status: {status.value.title()}")
    
    async def on_error(self, error: Exception) -> None:
        """Handle errors with detailed information."""
        print(f"\n❌ Error: {type(error).__name__}: {error}")


class MockProvider:
    """Mock provider for demonstration without requiring API keys."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger("MockProvider")
        
    async def initialize(self) -> None:
        """Simulate provider initialization."""
        await asyncio.sleep(0.5)  # Simulate initialization delay
        self.logger.info("Mock provider initialized")
    
    async def generate_response(self, messages: List[Message], stream: bool = True, **kwargs):
        """Generate mock responses that simulate real AI behavior."""
        from real_time_agent.core.interfaces import AgentResponse
        import uuid
        
        # Get the latest user message
        user_messages = [m for m in messages if m.type == MessageType.USER]
        latest_message = user_messages[-1].content.lower() if user_messages else ""
        
        # Generate contextual responses
        if "hello" in latest_message or "hi" in latest_message:
            response_text = ("Hello! I'm a mock AI assistant demonstrating the real-time agent "
                           "capabilities. I can help you understand how streaming responses work, "
                           "handle different types of conversations, and showcase the event-driven "
                           "architecture of this system.")
        elif "real-time" in latest_message or "agent" in latest_message:
            response_text = ("Real-time agents are AI systems that provide immediate, streaming "
                           "responses to user inputs. They're built on event-driven architectures "
                           "that enable low-latency interactions. Key features include: streaming "
                           "response generation, real-time event handling, connection management, "
                           "and scalable provider abstractions. This implementation supports both "
                           "Azure OpenAI and AI Foundry as backend providers.")
        elif "azure" in latest_message or "openai" in latest_message:
            response_text = ("Azure OpenAI is Microsoft's cloud-based implementation of OpenAI's "
                           "models, providing enterprise-grade security, compliance, and integration "
                           "with Azure services. It offers the same powerful GPT models with additional "
                           "features like private networking, customer-managed keys, and SLA guarantees. "
                           "Perfect for enterprise applications requiring both AI capabilities and "
                           "robust security measures.")
        elif "foundry" in latest_message or "ai foundry" in latest_message:
            response_text = ("AI Foundry is Microsoft's comprehensive platform for building, "
                           "deploying, and managing AI applications. It provides tools for model "
                           "development, training, fine-tuning, and deployment across various AI "
                           "scenarios. The platform supports both proprietary and open-source models, "
                           "offering flexibility in choosing the right AI solution for specific use cases.")
        elif "streaming" in latest_message:
            response_text = ("Streaming responses provide immediate feedback to users by sending "
                           "response chunks as they're generated, rather than waiting for the complete "
                           "response. This creates a more interactive experience, reduces perceived "
                           "latency, and keeps users engaged during longer responses. Implementation "
                           "involves async generators, event-driven architectures, and careful state "
                           "management to handle partial responses correctly.")
        else:
            response_text = (f"You asked about: '{latest_message}'. This is a mock response "
                           f"demonstrating how the real-time agent processes your input and generates "
                           f"contextual responses. In a real implementation, this would be powered by "
                           f"Azure OpenAI or AI Foundry models with much more sophisticated understanding "
                           f"and generation capabilities.")
        
        if stream:
            return self._stream_response(response_text)
        else:
            return self._single_response(response_text)
    
    async def _stream_response(self, response_text: str):
        """Generate streaming response."""
        from real_time_agent.core.interfaces import AgentResponse
        import uuid
        
        # Simulate streaming response
        message_id = str(uuid.uuid4())
        words = response_text.split()
        accumulated = ""
        
        for i, word in enumerate(words):
            accumulated += word + " "
            
            message = Message(
                id=message_id,
                type=MessageType.ASSISTANT,
                content=word + " ",
                timestamp=datetime.now(),
                metadata={
                    "accumulated_content": accumulated.strip(),
                    "is_streaming": True
                }
            )
            
            is_final = (i == len(words) - 1)
            
            yield AgentResponse(
                message=message,
                is_final=is_final,
                usage={"total_tokens": len(accumulated.split())} if is_final else None
            )
            
            # Simulate typing delay
            await asyncio.sleep(0.05)
    
    async def _single_response(self, response_text: str):
        """Generate single response."""
        from real_time_agent.core.interfaces import AgentResponse
        import uuid
        
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.ASSISTANT,
            content=response_text,
            timestamp=datetime.now(),
            metadata={"is_streaming": False}
        )
        
        yield AgentResponse(
            message=message,
            is_final=True,
            usage={"total_tokens": len(response_text.split())}
        )
    
    async def close(self) -> None:
        """Close the mock provider."""
        self.logger.info("Mock provider closed")


async def demonstrate_complete_workflow():
    """Demonstrate the complete real-time agent workflow."""
    
    print("🚀 Real-Time Agent Complete Workflow Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = AgentConfig(
        provider="mock",  # Using mock provider for demo
        max_tokens=500,
        temperature=0.7,
        streaming=True,
        system_prompt=(
            "You are a helpful AI assistant demonstrating real-time agent capabilities. "
            "Provide informative responses about real-time agents, Azure OpenAI, and AI Foundry."
        ),
        log_level="INFO"
    )
    
    print(f"\n📋 Configuration:")
    print(f"   Provider: {config.provider}")
    print(f"   Max Tokens: {config.max_tokens}")
    print(f"   Temperature: {config.temperature}")
    print(f"   Streaming: {config.streaming}")
    
    # Create components
    provider = MockProvider(config)
    event_handler = DemoEventHandler()
    agent = RealTimeAgent(config, provider, event_handler)
    
    try:
        # Initialize the agent
        print(f"\n🔧 Initializing agent...")
        await agent.initialize()
        
        # Set system prompt
        await agent.set_system_prompt(config.system_prompt)
        
        # Demo conversation
        demo_questions = [
            "Hello! Can you explain what real-time agents are?",
            "What are the benefits of using Azure OpenAI for real-time applications?",
            "How does streaming work in AI responses?",
            "Can you compare Azure OpenAI and AI Foundry?",
            "What are some best practices for implementing real-time agents?"
        ]
        
        print(f"\n💬 Starting conversation with {len(demo_questions)} questions...")
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n" + "─" * 60)
            print(f"Question {i}/{len(demo_questions)}")
            
            # Send message and handle streaming response
            if config.streaming:
                print(f"\n🙋 User: {question}")
                print(f"🤖 Assistant: ", end='', flush=True)
                
                async for response_chunk in await agent.send_message(question):
                    if response_chunk.is_final:
                        print()  # New line after streaming completes
                        if response_chunk.usage:
                            print(f"   📊 Tokens used: {response_chunk.usage.get('total_tokens', 0)}")
                        break
            else:
                response = await agent.send_message(question)
                print(f"\n🤖 Assistant: {response.message.content}")
            
            # Small delay between questions
            if i < len(demo_questions):
                await asyncio.sleep(1)
        
        # Demonstrate conversation management
        print(f"\n" + "=" * 60)
        print("📈 Conversation Summary")
        
        history = await agent.get_conversation_history()
        print(f"   Total messages: {len(history)}")
        
        user_messages = [m for m in history if m.type == MessageType.USER]
        assistant_messages = [m for m in history if m.type == MessageType.ASSISTANT]
        system_messages = [m for m in history if m.type == MessageType.SYSTEM]
        
        print(f"   User messages: {len(user_messages)}")
        print(f"   Assistant messages: {len(assistant_messages)}")
        print(f"   System messages: {len(system_messages)}")
        
        # Export conversation
        print(f"\n💾 Exporting conversation...")
        
        # Create temp directory if it doesn't exist
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        json_export = ConversationExporter.to_json(history, pretty=True)
        json_file = os.path.join(temp_dir, "demo_conversation.json")
        with open(json_file, 'w') as f:
            f.write(json_export)
        
        markdown_export = ConversationExporter.to_markdown(history)
        md_file = os.path.join(temp_dir, "demo_conversation.md")
        with open(md_file, 'w') as f:
            f.write(markdown_export)
        
        print(f"   JSON export: {json_file}")
        print(f"   Markdown export: {md_file}")
        
        # Demonstrate error handling
        print(f"\n🛠️  Testing error handling...")
        try:
            # This should work fine with mock provider
            await agent.send_message("Test error handling")
            print("   ✅ Error handling test passed")
        except Exception as e:
            print(f"   ❌ Error caught: {e}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📊 Final Statistics:")
        print(f"   Messages processed: {event_handler.message_count}")
        print(f"   Agent status: {agent.status.value}")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise
    finally:
        # Clean up
        await agent.close()
        print(f"\n🔒 Agent closed and resources cleaned up")


async def main():
    """Main function."""
    try:
        await demonstrate_complete_workflow()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())