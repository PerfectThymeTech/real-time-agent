"""Advanced example demonstrating streaming responses and event handling."""

import asyncio
import logging
from typing import List
from real_time_agent import RealTimeAgent, AgentConfig, AzureOpenAIProvider
from real_time_agent.core.interfaces import Message, MessageType, ConnectionStatus
from real_time_agent.utils.helpers import ConversationExporter


class AdvancedEventHandler:
    """Advanced event handler with custom logic."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.message_count = 0
        self.streaming_content = ""
        
    async def on_message(self, message: Message) -> None:
        """Handle incoming messages with advanced logic."""
        self.message_count += 1
        
        if message.type == MessageType.USER:
            self.logger.info(f"[{self.message_count}] User: {message.content}")
        elif message.type == MessageType.ASSISTANT:
            # For streaming responses, accumulate content
            if hasattr(message, 'metadata') and message.metadata:
                accumulated = message.metadata.get('accumulated_content', '')
                if accumulated:
                    # This is a streaming chunk
                    self.streaming_content = accumulated
                    print(f"\rAssistant: {accumulated}", end='', flush=True)
                else:
                    # This is a complete message
                    self.logger.info(f"[{self.message_count}] Assistant: {message.content}")
        elif message.type == MessageType.SYSTEM:
            self.logger.info(f"[{self.message_count}] System: {message.content}")
    
    async def on_connection_status(self, status: ConnectionStatus) -> None:
        """Handle connection status changes."""
        if status == ConnectionStatus.CONNECTED:
            self.logger.info("🟢 Agent connected and ready")
        elif status == ConnectionStatus.CONNECTING:
            self.logger.info("🟡 Agent connecting...")
        elif status == ConnectionStatus.DISCONNECTED:
            self.logger.info("🔴 Agent disconnected")
        elif status == ConnectionStatus.ERROR:
            self.logger.error("❌ Agent connection error")
        elif status == ConnectionStatus.RECONNECTING:
            self.logger.info("🔄 Agent reconnecting...")
    
    async def on_error(self, error: Exception) -> None:
        """Handle errors with detailed logging."""
        self.logger.error(f"❌ Error occurred: {type(error).__name__}: {error}")


async def demonstrate_streaming():
    """Demonstrate streaming responses with real-time feedback."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Configuration for streaming
    config = AgentConfig(
        provider="azure_openai",
        azure_openai_endpoint="https://your-resource.openai.azure.com/",
        azure_openai_deployment="gpt-4",
        max_tokens=800,
        temperature=0.8,
        streaming=True,
        system_prompt=(
            "You are an expert AI assistant specializing in real-time applications. "
            "Provide detailed, technical explanations with examples."
        )
    )
    
    # Create advanced components
    provider = AzureOpenAIProvider(config)
    event_handler = AdvancedEventHandler()
    agent = RealTimeAgent(config, provider, event_handler)
    
    try:
        # Initialize agent
        await agent.initialize()
        
        # Complex questions that benefit from streaming
        questions = [
            (
                "Explain the architecture of a real-time AI agent system, "
                "including the key components and data flow."
            ),
            (
                "What are the technical challenges in implementing streaming "
                "responses for AI agents, and how can they be addressed?"
            ),
            (
                "Provide a detailed comparison between Azure OpenAI and "
                "AI Foundry for real-time agent applications."
            )
        ]
        
        conversation_messages: List[Message] = []
        
        for i, question in enumerate(questions, 1):
            logger.info(f"\\n--- Question {i} ---")
            logger.info(f"User: {question}")
            
            print("\\nAssistant: ", end='', flush=True)
            
            # Process streaming response
            full_response = ""
            async for response_chunk in await agent.send_message(question):
                if response_chunk.is_final:
                    full_response = response_chunk.message.metadata.get(
                        'accumulated_content', 
                        response_chunk.message.content
                    )
                    print()  # New line after streaming
                    break
            
            # Add a pause between questions
            if i < len(questions):
                await asyncio.sleep(2)
        
        # Export conversation
        history = await agent.get_conversation_history()
        
        # Export to different formats
        json_export = ConversationExporter.to_json(history)
        markdown_export = ConversationExporter.to_markdown(history)
        
        # Save exports
        with open('/tmp/conversation.json', 'w') as f:
            f.write(json_export)
        
        with open('/tmp/conversation.md', 'w') as f:
            f.write(markdown_export)
        
        logger.info(f"\\n--- Conversation Summary ---")
        logger.info(f"Total messages: {len(history)}")
        logger.info(f"Conversation exported to /tmp/conversation.json and /tmp/conversation.md")
        
    except Exception as e:
        logger.error(f"Error in streaming demonstration: {e}")
        raise
    finally:
        await agent.close()


async def demonstrate_error_handling():
    """Demonstrate error handling and recovery."""
    logger = logging.getLogger(__name__)
    
    # Configuration with intentional issues for testing
    config = AgentConfig(
        provider="azure_openai",
        azure_openai_endpoint="https://invalid-endpoint.com/",  # Invalid endpoint
        azure_openai_deployment="invalid-model",
        max_tokens=100,
        temperature=0.5,
        streaming=False
    )
    
    provider = AzureOpenAIProvider(config)
    event_handler = AdvancedEventHandler()
    agent = RealTimeAgent(config, provider, event_handler)
    
    try:
        # This should fail and demonstrate error handling
        await agent.initialize()
    except Exception as e:
        logger.info(f"Expected error caught: {type(e).__name__}: {e}")
        logger.info("Error handling demonstration completed")


async def main():
    """Main function to run all demonstrations."""
    print("=== Real-Time Agent Advanced Example ===\\n")
    
    try:
        print("1. Demonstrating streaming responses...")
        await demonstrate_streaming()
        
        print("\\n2. Demonstrating error handling...")
        await demonstrate_error_handling()
        
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Note: Make sure to configure your Azure OpenAI credentials!")


if __name__ == "__main__":
    asyncio.run(main())