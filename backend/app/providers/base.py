from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolCall(BaseModel):
    id: Optional[str] = None
    name: str
    arguments: Dict[str, Any]


class LLMMessage(BaseModel):
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    model_name: str = ""
    provider_name: str = ""
    raw_response: Optional[Dict[str, Any]] = None


class BaseModelProvider(ABC):
    """Abstract base class for all LLM model providers."""

    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> LLMResponse:
        """Generate a response or tool calls given a message history and tool definitions."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider and configured model are currently reachable."""
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int, pricing: Optional[Dict[str, float]] = None) -> float:
        """Calculate estimated cost in USD."""
        if not pricing:
            return 0.0
        input_rate = pricing.get("input", pricing.get("input_cost_per_million", 0.0)) / 1_000_000.0
        output_rate = pricing.get("output", pricing.get("output_cost_per_million", 0.0)) / 1_000_000.0
        return round((input_tokens * input_rate) + (output_tokens * output_rate), 6)
