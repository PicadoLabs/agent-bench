from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from app.providers.base import BaseModelProvider
from app.sandbox.base import BaseSandbox


class AgentRunResult(BaseModel):
    success: bool
    status: str  # SUCCEEDED, PARTIAL, FAILED, TIMEOUT, CRASHED
    total_steps: int = 0
    tool_calls_count: int = 0
    retries_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    final_output: str = ""
    error_message: Optional[str] = None
    git_diff: str = ""


# Event callback type: async (event_type: str, message: str, details: dict) -> None
EventCallback = Optional[Callable[[str, str, Dict[str, Any]], Awaitable[None]]]


class BaseAgent(ABC):
    """Abstract interface for all coding agents evaluated by AgentBench."""

    def __init__(self, name: str, provider: BaseModelProvider, max_steps: int = 20, max_retries: int = 3):
        self.name = name
        self.provider = provider
        self.max_steps = max_steps
        self.max_retries = max_retries

    @abstractmethod
    async def run(
        self,
        task_prompt: str,
        sandbox: BaseSandbox,
        constraints: Optional[str] = None,
        test_command: str = "pytest",
        on_event: EventCallback = None
    ) -> AgentRunResult:
        """Execute the agent loop on the task inside the given sandbox."""
        pass
