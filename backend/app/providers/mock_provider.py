import asyncio
from typing import List, Dict, Any, Optional
from app.providers.base import BaseModelProvider, LLMMessage, LLMResponse, ToolDefinition, ToolCall


class MockProvider(BaseModelProvider):
    """
    Deterministic Mock Provider for CI/CD, offline benchmarks, and automated E2E tests.
    Can be configured with scripted responses or intelligent fallback heuristics.
    """

    def __init__(self, model_name: str = "mock-coder", script: Optional[List[LLMResponse]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
        self.script = script or []
        self.call_count = 0

    async def is_available(self) -> bool:
        return True

    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> LLMResponse:
        # Simulate slight async processing time
        await asyncio.sleep(0.05)

        if self.script and self.call_count < len(self.script):
            resp = self.script[self.call_count]
            self.call_count += 1
            return resp

        self.call_count += 1

        # Heuristic response based on conversation history
        last_msg = messages[-1] if messages else LLMMessage(role="user", content="")
        
        # If last message was tool result from test run
        if last_msg.role == "tool" or "test" in last_msg.content.lower():
            return LLMResponse(
                content="I have investigated the codebase, located the bug, and applied the necessary patch. All tests now execute successfully.",
                tool_calls=[],
                input_tokens=150,
                output_tokens=40,
                total_tokens=190,
                model_name=self.model_name,
                provider_name="mock"
            )

        # Default: list files or read target file
        if tools and any(t.name == "list_files" for t in tools) and self.call_count == 1:
            return LLMResponse(
                content="Let's inspect the repository directory structure first.",
                tool_calls=[ToolCall(name="list_files", arguments={"path": "."})],
                input_tokens=100,
                output_tokens=25,
                total_tokens=125,
                model_name=self.model_name,
                provider_name="mock"
            )

        return LLMResponse(
            content="Task completed successfully.",
            tool_calls=[],
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            model_name=self.model_name,
            provider_name="mock"
        )
