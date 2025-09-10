"""Basic example of using the real-time agent with Azure OpenAI."""

import asyncio
import logging
from real_time_agent import RealTimeAgent, AgentConfig, AzureOpenAIProvider
from real_time_agent.utils.helpers import LoggingEventHandler


async def main():
    """Basic example of real-time agent usage."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create configuration
        config = AgentConfig(
            provider="azure_openai",
            azure_openai_endpoint="https://your-resource.openai.azure.com/",
            azure_openai_deployment="gpt-4",
            azure_openai_api_key="your-api-key",  # Or use environment variable
            max_tokens=500,
            temperature=0.7,
            streaming=True,
            system_prompt="You are a helpful AI assistant. Provide concise and accurate responses."
        )
        
        # Create provider and event handler
        provider = AzureOpenAIProvider(config)
        event_handler = LoggingEventHandler(logger)
        
        # Create and initialize agent
        agent = RealTimeAgent(config, provider, event_handler)
        await agent.initialize()
        
        logger.info("Real-time agent initialized successfully!")
        
        # Set up the system prompt
        await agent.set_system_prompt(config.system_prompt)
        
        # Example conversation
        messages = [
            "Hello! Can you help me understand what real-time agents are?",
            "What are the benefits of using Azure OpenAI for real-time applications?",
            "Can you provide a simple example of how to implement streaming responses?"
        ]
        
        for user_message in messages:
            logger.info(f"User: {user_message}")
            
            # Send message and handle response
            if config.streaming:
                # Handle streaming response
                async for response_chunk in await agent.send_message(user_message):
                    if response_chunk.is_final:
                        logger.info(f"Assistant: {response_chunk.message.content}")
                        break
            else:
                # Handle single response
                response = await agent.send_message(user_message)
                logger.info(f"Assistant: {response.message.content}")
            
            # Small delay between messages
            await asyncio.sleep(1)
        
        # Get conversation history
        history = await agent.get_conversation_history()
        logger.info(f"Conversation completed with {len(history)} messages")
        
    except Exception as e:
        logger.error(f"Error in example: {e}")
        raise
    finally:
        # Clean up
        if 'agent' in locals():
            await agent.close()


if __name__ == "__main__":
    asyncio.run(main())