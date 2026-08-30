import json
import httpx
import re
from typing import List, Dict, Any, Optional
from app.providers.base import BaseModelProvider, LLMMessage, LLMResponse, ToolDefinition, ToolCall


class OllamaProvider(BaseModelProvider):
    """Local-first Ollama provider with zero-cost execution and structured tool calling."""

    def __init__(self, model_name: str = "qwen2.5-coder", base_url: str = "http://localhost:11434", config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
        self.base_url = base_url.rstrip("/")

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                    model_base = self.model_name.split(":")[0]
                    return any(model_base in m for m in models) or len(models) > 0
                return False
        except Exception:
            return False

    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> LLMResponse:
        ollama_messages = []
        for m in messages:
            msg_dict = {"role": m.role, "content": m.content}
            ollama_messages.append(msg_dict)

        ollama_tools = None
        if tools:
            ollama_tools = [
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

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if ollama_tools:
            payload["tools"] = ollama_tools

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                res.raise_for_status()
                data = res.json()

            msg = data.get("message", {})
            content = msg.get("content", "")
            raw_tool_calls = msg.get("tool_calls", [])

            parsed_tool_calls: List[ToolCall] = []
            for tc in raw_tool_calls:
                fn = tc.get("function", {})
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}
                parsed_tool_calls.append(ToolCall(
                    id=tc.get("id"),
                    name=fn.get("name", "unknown_tool"),
                    arguments=args
                ))

            # Fallback regex parsing if model returned JSON in content instead of tool_calls field
            if not parsed_tool_calls and tools and content:
                parsed_tool_calls = self._extract_json_tool_calls(content, tools)

            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)

            return LLMResponse(
                content=content,
                tool_calls=parsed_tool_calls,
                input_tokens=prompt_eval_count,
                output_tokens=eval_count,
                total_tokens=prompt_eval_count + eval_count,
                model_name=self.model_name,
                provider_name="ollama",
                raw_response=data
            )
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed ({self.model_name} at {self.base_url}): {str(e)}")

    def _extract_json_tool_calls(self, text: str, available_tools: List[ToolDefinition]) -> List[ToolCall]:
        tool_names = {t.name for t in available_tools}
        calls = []
        
        # 1. Look for <tool_call> ... </tool_call> tags
        xml_matches = re.findall(r"<tool_call>([\s\S]*?)</tool_call>", text)
        for xml_block in xml_matches:
            try:
                obj = json.loads(xml_block.strip())
                if isinstance(obj, dict):
                    name = obj.get("name") or obj.get("tool")
                    if name in tool_names:
                        args = obj.get("arguments") or obj.get("parameters") or obj.get("input") or {}
                        calls.append(ToolCall(name=name, arguments=args))
            except Exception:
                pass

        if calls:
            return calls

        # 2. Look for code fences with json or tool_call
        json_blocks = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
        for block in json_blocks:
            try:
                obj = json.loads(block)
                if isinstance(obj, dict):
                    name = obj.get("name") or obj.get("tool")
                    if name in tool_names:
                        args = obj.get("arguments") or obj.get("parameters") or obj.get("input") or {}
                        calls.append(ToolCall(name=name, arguments=args))
                    elif "path" in obj and "content" in obj and "write_file" in tool_names:
                        calls.append(ToolCall(name="write_file", arguments={"path": obj["path"], "content": obj["content"]}))
            except Exception:
                continue

        if calls:
            return calls

        # 3. Look for standalone JSON objects in text
        json_candidates = re.findall(r"(\{\s*\"(?:name|tool)\"\s*:\s*\"[^\"]+\"[\s\S]*?\})", text)
        for cand in json_candidates:
            try:
                obj = json.loads(cand)
                if isinstance(obj, dict):
                    name = obj.get("name") or obj.get("tool")
                    if name in tool_names:
                        args = obj.get("arguments") or obj.get("parameters") or obj.get("input") or {}
                        calls.append(ToolCall(name=name, arguments=args))
            except Exception:
                continue

        return calls
