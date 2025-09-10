# Declarative Agent Definitions

This document provides an overview of how to define AI agents using a declarative approach. By using configuration files, users can easily create, modify, and manage agents without needing to write extensive code. This approach promotes reusability, maintainability, and scalability in building AI-driven applications.

This also acknowledges the requirement for organizations to manage agents at scale, allowing for consistent configurations and easier updates across multiple agents without having to modify code directly for every minor change or update.

![Declarative Agent Definitions Diagram](/docs/images/declaritive-agents.png)

## Declarative Configuration

The declarative configuration is typically done using YAML or JSON files and must cover the following aspects:

- **Community**: In complex multi-agent scenarios you may end up with a large number of agents focussed on very specific tasks. To ensure that agents can collaborate effectively, we introduce the concept of communities. Communities are groups of agents that share common goals, knowledge, or functionalities. Agents within a community can communicate and collaborate more efficiently, leveraging shared resources and expertise.
- **Task**. The agent's task defines the mission and target of this specific agent which will be used to identify handover scenarios based on the end-user queries to ensure the session context can be updated accordingly.
- **Tools**: Define the tools and APIs the agent can use to accomplish its tasks. This includes specifying the tool's name, description, input parameters, and expected outputs.
- **Instructions**: Define the prompt templates that guide the agent's interactions. This includes system messages, user messages, and any other contextual information needed to generate appropriate responses. Some pre-defined placeholders can be used to insert dynamic content into the prompts, such as the task list, conversation flows, or context-specific information.
- **Conversation Flows**: Define the conversation flows that outline how the agent should interact with users. This includes specifying the sequence of states, decision points, and sample responses. Placeholders can be used to insert dynamic states and transitions into the conversation flows
- **Transition States**: Define to which other community the agent can handover the session in case the task is outside of its scope. This ensures that the end-user query can be handled by the most appropriate agent while maintaining the session context.

A sample declarative configuration in YAML format is shown below:

```yaml
agent:
  name: "CustomerSupportAgent"
  community: "CustomerSupport"
  task: "Assist customers with product inquiries and support issues."
  tools:
    - name: "ProductInfoAPI"
      description: "Fetch product information from the database."
      input_parameters:
        - product_id: "string"
      output: "Product details in JSON format."
    - name: "SupportTicketAPI"
      description: "Create and manage support tickets."
      input_parameters:
        - customer_id: "string"
        - issue_description: "string"
      output: "Ticket ID and status."
  instructions:
    system_message: |
      You are a helpful customer support agent. Your task is to assist customers with their inquiries and support issues.
    user_message_template: |
      Customer Query: {user_query}
      Available Tools: {tools_list}
      Please provide a response based on the customer's query and available tools.
  conversation_flows:
    - state: "Greeting"
      description: "Initial greeting and understanding user intent."
      instructions: [
        "Greet the user and ask how you can assist them today."
      ]
      examples: [
        "Hello! How can I assist you today?",
        "Hi there! What can I help you with?"
      ]
      transitions:
        - condition: "ProductInquiry"
          next_state: "ProductInfo"
        - condition: "SupportIssue"
          next_state: "SupportTicket"
    - state: "ProductInfo"
      prompt: "Please provide the product ID you would like information about."
      transitions:
        - user_provides_product_id:
            next_state: "FetchProductInfo"
    - state: "FetchProductInfo"
      description: "Fetch product information from the database."
      instructions: [
        "Call ProductInfoAPI with provided product_id",
        "Provide the product details to the user"
      ]
      examples: [
        "The product details are as follows: {product_details}"
      ]
      transitions:
        - condition: "ProductDetailsProvided"
          next_state: "EndConversation"
        - condition: "UserNeedsMoreInfo"
          next_state: "ProductInfo"
    - state: "SupportTicket"
      description: "Assist the user with creating a support ticket."
      instructions: [
        "Ask the user for their customer ID and a description of the issue they are facing."
      ]
      examples: [
        "Can you please provide your customer ID and describe the issue you're facing?"
      ]
      transitions:
        - condition: "UserProvidesCustomerID"
          next_state: "CreateSupportTicket"
    - state: "CreateSupportTicket"
      description: "Create a support ticket using the SupportTicketAPI."
      instructions: [
        "Call SupportTicketAPI with customer_id and issue_description"
      ]
      examples: [
        "Your support ticket has been created. The ticket ID is {ticket_id}."
      ]
      transitions:
        - condition: "UserSatisfied"
          next_state: "EndConversation"
        - condition: "UserNeedsMoreHelp"
          next_state: "SupportTicket"
    - state: "{end_conversation_state}"
  transition_states:
    - community: "Sales"
      condition: "user_intent == 'PurchaseInquiry'"
    - community: "TechnicalSupport"
      condition: "user_intent == 'TechnicalIssue'"
```

## Agent Map

The declarative configurations are stored in a central repository or database, allowing for easy access and management. The agents are loaded dynamically at runtime.

Internally, the agent definitions are parsed and converted into executable agents using a framework like the OpenAI Agents SDK. When loaded, these communities and agents form a directed cyclic graph where nodes represent agents and edges represent possible transitions between agents based on user queries.

An agent map is maintained to keep track of all defined agents, their communities, tasks, and available tools. This map helps in routing user queries to the appropriate agent based on the task and community.
