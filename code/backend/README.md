# Real-time backend

This folder contains the backend code for the real-time AI agents. The backend is responsible for communicating with the real-time API, loading agent definitions, configurations, and states. It also defines the business logic for MCP tool calling and function calls to keep the logic private and client-agnostic while ensuring low latency.

The backend will be built using Python and FastAPI, leveraging asynchronous programming to handle real-time interactions efficiently. It will also include components for session state management, observability, and security.

The backend will be designed to be modular and extensible, allowing for easy integration with different real-time model providers such as Azure OpenAI and AI Foundry. The architecture will also support multi-modal inputs and outputs, ensuring a seamless user experience across various interaction modes.

For more details on the conceptual architecture, please refer to the [Conceptual Architecture Document](/docs/ConceptualArchitecture.md).
