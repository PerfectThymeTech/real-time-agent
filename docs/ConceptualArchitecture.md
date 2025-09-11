# Conceptual Architecture

This document provides an overview of the conceptual architecture for building real-time AI agents using Azure OpenAI or AI Foundry. The architecture is designed to support latency-sensitive scenarios, multi-modal inputs and outputs, and scalability for production use cases.

![Conceptual Architecture Diagram](/docs/images/architecture-conceptual.png)

## Key Components

1. **Client**: The front-end application that interacts with users, capturing multi-modal inputs (text, voice, images) and displaying real-time streaming responses.
2. **AI Foundry / Azure OpenAI / Real-time model**: The core AI service that processes inputs and generates responses using advanced real-time language models.
3. **Application Backend**: The backend service that manages agent definitions, configurations, and states. It also defines the business logic for MCP tool calling and function calls to keep the logic private and client-agnostic while ensuring low latency.
4. **Session State Management**: Manages the state of each user session, ensuring continuity and context for multi-turn conversations across sessions.
5. **MCP Server**: Model context protocol is used as the default protocol for tool calling and function call scenarios. It allows the agent to interact with external tools and services in a structured and consistent and resilient manner.
6. **Observability Framework**: Provides logging, monitoring, and tracing capabilities to ensure system reliability and performance across all agents.
7. **Testing**: A comprehensive testing framework to validate the functionality, performance, and reliability of the agents in various scenarios (text and audio-based evaluations).
8. **Security and Compliance**: Ensures data handling best practices are followed by default, including encryption, access controls, and compliance with relevant regulations.

## Flow of Interactions

1. When using Web RTC, the client establishes a connection with the backend to fetch an ephemeral token for authentication.
2. The client establishes a direct connection with the AI Foundry or Azure OpenAI service using the token over the Web RTC or SIP API interface.
3.  The API triggers the Webhook API which then sends a webhook to the application backend webhook URL to notify the backend of the new session.
4. The application backend initializes a WebSocket connection with the Realtime API which will be active throughout the session.
5. The client sends multi-modal inputs (text, voice, images) to the AI Foundry or Azure OpenAI service.
6. The AI Foundry or Azure OpenAI service processes the inputs and generates real-time streaming responses. It also informs the backend of the real-time events via the WebSocket connection.
7. The application backend manages the agent's state and handles any tool calls or function calls using the MCP protocol. The application backend can also send messages to the AI Foundry or Azure OpenAI service via the WebSocket connection to provide results from the tool calls or function calls.
8. The client receives and displays the real-time streaming responses to the user.
9. The observability framework captures logs, metrics, and traces throughout the interaction to monitor performance and reliability in real-time based on LLM-as-a-judge metrics.
10. The session state management component ensures continuity and context for multi-turn conversations across sessions.

## Real-time model

We want to build the solution in a way that allows us to easily swap out the real-time model provider, whether it's Azure OpenAI, AI Foundry, or any other service that supports real-time streaming and multi-modal capabilities. This abstraction layer will ensure that our architecture remains flexible and adaptable to future advancements in AI technology.

Due to the fact that only few model providers currently support real-time audio streaming and multi-modal capabilities, we will initially focus on integrating with Azure OpenAI and AI Foundry. However, in the architecture design we want to accommodate additional providers as they become available, ensuring that we can leverage the best available technology for our use cases.
