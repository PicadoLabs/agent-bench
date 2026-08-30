import json
import httpx
from typing import List, Dict, Any, Optional
from app.providers.base import BaseModelProvider, LLMMessage, LLMResponse, ToolDefinition, ToolCall


class GeminiProvider(BaseModelProvider):
    """Google Gemini provider via REST API."""

    def __init__(self, model_name: str = "gemini-1.5-pro", api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

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
            raise ValueError("Gemini API key is missing. Please configure GEMINI_API_KEY.")

        contents = []
        system_instruction = None

        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            elif m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == "assistant":
                parts: List[Dict[str, Any]] = []
                if m.content:
                    parts.append({"text": m.content})
                if m.tool_calls:
                    for tc in m.tool_calls:
                        parts.append({"functionCall": {"name": tc.name, "args": tc.arguments}})
                contents.append({"role": "model", "parts": parts})
            elif m.role == "tool":
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": m.tool_call_id or "tool_call",
                            "response": {"result": m.content}
                        }
                    }]
                })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        if tools:
            payload["tools"] = [{
                "functionDeclarations": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters
                    }
                    for t in tools
                ]
            }]

        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return LLMResponse(content="", model_name=self.model_name, provider_name="gemini")

        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        content_text = ""
        parsed_tool_calls: List[ToolCall] = []

        for p in parts:
            if "text" in p:
                content_text += p["text"]
            if "functionCall" in p:
                fc = p["functionCall"]
                parsed_tool_calls.append(ToolCall(
                    name=fc.get("name", ""),
                    arguments=fc.get("args", {})
                ))

        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        candidates_tokens = usage.get("candidatesTokenCount", 0)

        return LLMResponse(
            content=content_text if content_text else None,
            tool_calls=parsed_tool_calls,
            input_tokens=prompt_tokens,
            output_tokens=candidates_tokens,
            total_tokens=prompt_tokens + candidates_tokens,
            model_name=self.model_name,
            provider_name="gemini",
            raw_response=data
        )
