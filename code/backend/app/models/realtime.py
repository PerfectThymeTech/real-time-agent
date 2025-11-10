from pydantic import BaseModel, Field


class HandoffConfig(BaseModel):
    agent_name: str = Field(..., description="Specifies the name of the agent to hand off to.")
    condition: str = Field(..., description="Specifies the condition under which the handoff occurs.", required=True)


class AgentConfig(BaseModel):
    name: str = Field(..., description="Specifies the name of the agent.")
    community: str = Field(..., description="Specifies which community the agent is part of.")
    opener: bool = Field(..., description="Specifies whether the agent should be the first of every session")
    instructions: str = Field(..., description="Specifies the instructions guiding the agent's behavior.")
    tools: list[str] = Field(default_factory=list, description="Specifies the list of tools available to the agent.")
    mcp_server: list[str] = Field(..., description="Specifies the list of mcp servers available to the agent.")
    handoffs: list[HandoffConfig] = Field(default=[], description="Specifies the list of handoffs available to the agent.")
    output_guardrails: list[str] = Field(default_factory=list, description="Specifies the output guardrails for the agent.")
