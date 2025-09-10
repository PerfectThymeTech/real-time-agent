# Azure Architecture

This document provides an overview of the Azure architecture for building real-time AI agents using Azure OpenAI or AI Foundry. The architecture is designed to support latency-sensitive scenarios, multi-modal inputs and outputs, and scalability for production use cases.

![Azure Architecture Diagram](/docs/images/architecture-azure.png)

## Key Components

- **AI Foundry**: AI Foundry will be used to host the real-time models and manage the interactions between the client and the application backend.
- **Azure Container Apps / Azure Kubernetes Service (AKS)**: The application backend as well as the required MCP servers will be hosted on a container runtime in Azure. For reduced management overhead we consider the usage of Azure Container Apps. Alternatively, we will rely on AKS, providing a scalable and managed environment for running the backend services.
- **Azure Cosmos DB**: A globally distributed, multi-model database service will be used to store session states, and other relevant data.

## Observability

All observability integrations will rely on Open Telemetry to ensure a consistent and vendor-agnostic approach to monitoring and tracing. The observability framework will be integrated into the application backend and other components to provide comprehensive insights into system performance and reliability. Open Telemetry will also be used to capture agent specific metrics, logs, and traces.

Logs will be collected and stored in Azure Monitor Logs, providing a centralized location for log data analysis and visualization. Metrics will be captured and visualized using Azure Monitor Metrics, allowing for real-time monitoring of system performance. Traces will be collected and analyzed using Azure Monitor Application Insights, enabling end-to-end tracing of requests and interactions across the system.

Agent specific traces will be captured and visualized in a purpose-built tool like Langfuse, Confident AI or similar tools to provide insights into agent behavior and performance. This will allow for detailed analysis of agent interactions, decision-making processes, and overall effectiveness in handling user requests.

## Agent Tests

Comprehensive tests will be implemented to validate the functionality, performance, and reliability of the agents in various scenarios. These tests will cover both text and audio-based evaluations to ensure that the agents can effectively handle multi-modal inputs and outputs. The tests will be designed to simulate real-world scenarios, including latency-sensitive interactions, multi-turn conversations, and tool calling or function call scenarios. Edge cases and failure scenarios will also be included to ensure robustness and resilience of the agents.

## Realtime Backend

The application backend will be implemented using Python and FastAPI, providing a high-performance and scalable framework for building the backend services. The backend will manage agent definitions, configurations, and states, as well as handle business logic for MCP tool calling and function calls. We are considering different candidates for the integration with AI Foundry or Azure OpenAI. The following frameworks are currently under evaluation:

- **Open AI SDK**: The Open AI SDK provides low-level access to the underlying components, allowing for greater control and customization of the implementation. This approach offers more flexibility in terms of adapting to specific requirements and use cases. However, it also means that we will need to handle more of the implementation details ourselves, which may increase development time and complexity. Updates are usually faster compared to the Open AI Agents SDK.
- **Open AI Agents SDK**: The Open AI Agents SDK provides a higher-level abstraction over basic components which simplifies the development of AI agents. However, this also means that we have less control over the underlying implementation and may face limitations in terms of customization and flexibility. Also, in case of new features, we may need to wait for updates to the SDK before we can take advantage of them. Updates are usually slower compared to the Open AI SDK.
- **Agents Framework**: tbd
