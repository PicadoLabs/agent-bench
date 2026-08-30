import json
import httpx
from typing import List, Dict, Any, Optional
from app.providers.base import BaseModelProvider, LLMMessage, LLMResponse, ToolDefinition, ToolCall


class OpenAIProvider(BaseModelProvider):
    """OpenAI / OpenAI-compatible provider with structured tool calls."""

    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1", config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
                return res.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Please configure OPENAI_API_KEY.")

        openai_messages = []
        for m in messages:
            msg_dict: Dict[str, Any] = {"role": m.role, "content": m.content}
            if m.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id or f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else str(tc.arguments)
                        }
                    }
                    for i, tc in enumerate(m.tool_calls)
                ]
            if m.tool_call_id:
                msg_dict["tool_call_id"] = m.tool_call_id
            openai_messages.append(msg_dict)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters
                    }
                }
                for t in tools
            ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()

        choice = data["choices"][0]
        msg = choice.get("message", {})
        content = msg.get("content")

        parsed_tool_calls: List[ToolCall] = []
        for tc in msg.get("tool_calls", []):
            fn = tc.get("function", {})
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except Exception:
                args = {"raw": fn.get("arguments", "")}
            parsed_tool_calls.append(ToolCall(
                id=tc.get("id"),
                name=fn.get("name", ""),
                arguments=args
            ))

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        return LLMResponse(
            content=content,
            tool_calls=parsed_tool_calls,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model_name=self.model_name,
            provider_name="openai",
            raw_response=data
        )
