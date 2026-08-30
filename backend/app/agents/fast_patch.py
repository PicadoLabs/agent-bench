import json
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent, AgentRunResult, EventCallback
from app.agents.tools import ToolRegistry, ToolExecutionResult
from app.providers.base import LLMMessage
from app.sandbox.base import BaseSandbox

FAST_PATCH_SYSTEM_PROMPT = """You are a fast, single-pass automated patching agent.
Your objective is to quickly inspect the provided task, formulate a direct fix, and apply it immediately using write_file.
"""


class FastPatchAgent(BaseAgent):
    """
    Fast, low-latency patching agent that inspects files and applies a rapid fix
    in 1-2 turns with minimal exploration.
    """

    async def run(
        self,
        task_prompt: str,
        sandbox: BaseSandbox,
        constraints: Optional[str] = None,
        test_command: str = "pytest",
        on_event: EventCallback = None
    ) -> AgentRunResult:
        async def emit(event_type: str, msg: str, details: Dict[str, Any] = None):
            if on_event:
                await on_event(event_type, msg, details or {})

        await emit("agent_started", f"Starting FastPatchAgent on task", {"model": self.provider.model_name})

        files = await sandbox.list_files(".")
        await emit("tool_call", "Listing repository files", {"files": files})

        # Read relevant files to provide direct context
        file_contexts = {}
        for f in files:
            if f.endswith(".py") and not f.startswith("test_") and not f.endswith("_test.py"):
                try:
                    content = await sandbox.read_file(f)
                    file_contexts[f] = content
                except Exception:
                    pass

        prompt = f"""Task: {task_prompt}
Files: {files}
Constraints: {constraints or 'None'}

Source Code:
{json.dumps(file_contexts, indent=2)}

Provide the fix by calling write_file to save the modified code.
"""
        messages = [
            LLMMessage(role="system", content=FAST_PATCH_SYSTEM_PROMPT),
            LLMMessage(role="user", content=prompt)
        ]

        tools = ToolRegistry.get_tool_definitions()

        try:
            resp = await self.provider.generate(messages=messages, tools=tools, max_tokens=4096)
            tool_calls_count = 0
            if resp.tool_calls:
                for tc in resp.tool_calls:
                    tool_calls_count += 1
                    await emit("tool_call", f"FastPatch applying: {tc.name}", {"tool": tc.name, "arguments": tc.arguments})
                    await ToolRegistry.execute_tool(sandbox=sandbox, tool_name=tc.name, arguments=tc.arguments)

            git_diff = await sandbox.get_git_diff()
            await emit("agent_finished", "FastPatchAgent completed execution.", {})

            return AgentRunResult(
                success=True,
                status="SUCCEEDED" if tool_calls_count > 0 else "PARTIAL",
                total_steps=1,
                tool_calls_count=tool_calls_count,
                retries_count=0,
                input_tokens=resp.input_tokens,
                output_tokens=resp.output_tokens,
                total_tokens=resp.total_tokens,
                final_output=resp.content or "",
                git_diff=git_diff
            )
        except Exception as e:
            return AgentRunResult(
                success=False,
                status="CRASHED",
                total_steps=1,
                error_message=str(e),
                git_diff=await sandbox.get_git_diff()
            )

