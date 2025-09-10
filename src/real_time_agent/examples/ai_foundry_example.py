"""Example showing AI Foundry integration."""

import asyncio
import logging
from real_time_agent import RealTimeAgent, AgentConfig, AIFoundryProvider
from real_time_agent.utils.helpers import LoggingEventHandler


async def main():
    """Example using AI Foundry provider."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create configuration for AI Foundry
        config = AgentConfig(
            provider="ai_foundry",
            ai_foundry_endpoint="https://your-foundry-endpoint.com/",
            ai_foundry_api_key="your-foundry-api-key",  # Or use environment variable
            max_tokens=500,
            temperature=0.7,
            streaming=True,
            system_prompt="You are an AI assistant powered by AI Foundry. Be helpful and informative."
        )
        
        # Create provider and event handler
        provider = AIFoundryProvider(config)
        event_handler = LoggingEventHandler(logger)
        
        # Create and initialize agent
        agent = RealTimeAgent(config, provider, event_handler)
        await agent.initialize()
        
        logger.info("AI Foundry agent initialized successfully!")
        
        # Example conversation focused on AI Foundry capabilities
        messages = [
            "What is AI Foundry and how does it differ from other AI platforms?",
            "Can you explain the benefits of using AI Foundry for enterprise applications?",
            "What are some best practices for deploying AI agents using AI Foundry?"
        ]
        
        for user_message in messages:
            logger.info(f"User: {user_message}")
            
            # Send message and handle response
            if config.streaming:
                # Handle streaming response
                response_text = ""
                async for response_chunk in await agent.send_message(user_message):
                    response_text += response_chunk.message.content
                    if response_chunk.is_final:
                        logger.info(f"Assistant: {response_text}")
                        break
            else:
                # Handle single response
                response = await agent.send_message(user_message)
                logger.info(f"Assistant: {response.message.content}")
            
            # Small delay between messages
            await asyncio.sleep(1)
        
        # Get and display conversation summary
        history = await agent.get_conversation_history()
        logger.info(f"Conversation completed with {len(history)} messages using AI Foundry")
        
    except Exception as e:
        logger.error(f"Error in AI Foundry example: {e}")
        raise
    finally:
        # Clean up
        if 'agent' in locals():
            await agent.close()


if __name__ == "__main__":
    asyncio.run(main())