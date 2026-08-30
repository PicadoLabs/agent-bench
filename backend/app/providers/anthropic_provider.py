import json
import httpx
from typing import List, Dict, Any, Optional
from app.providers.base import BaseModelProvider, LLMMessage, LLMResponse, ToolDefinition, ToolCall


class AnthropicProvider(BaseModelProvider):
    """Anthropic Claude provider with native tool use."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("Anthropic API key is missing. Please configure ANTHROPIC_API_KEY.")

        system_prompt = ""
        anthropic_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            elif m.role == "tool":
                anthropic_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": m.tool_call_id or "tool_call",
                            "content": m.content
                        }
                    ]
                })
            elif m.role == "assistant" and m.tool_calls:
                blocks = []
                if m.content:
                    blocks.append({"type": "text", "text": m.content})
                for tc in m.tool_calls:
                    blocks.append({
                        "type": "tool_use",
                        "id": tc.id or "call_0",
                        "name": tc.name,
                        "input": tc.arguments
                    })
                anthropic_messages.append({"role": "assistant", "content": blocks})
            else:
                anthropic_messages.append({"role": m.role, "content": m.content})

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()

        if tools:
            payload["tools"] = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.parameters
                }
                for t in tools
            ]

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(f"{self.base_url}/messages", json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()

        content_text = ""
        parsed_tool_calls: List[ToolCall] = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                content_text += block.get("text", "")
            elif block.get("type") == "tool_use":
                parsed_tool_calls.append(ToolCall(
                    id=block.get("id"),
                    name=block.get("name"),
                    arguments=block.get("input", {})
                ))

        usage = data.get("usage", {})
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)

        return LLMResponse(
            content=content_text if content_text else None,
            tool_calls=parsed_tool_calls,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model_name=self.model_name,
            provider_name="anthropic",
            raw_response=data
        )
