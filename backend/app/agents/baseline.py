import json
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent, AgentRunResult, EventCallback
from app.agents.tools import ToolRegistry
from app.providers.base import LLMMessage
from app.sandbox.base import BaseSandbox


class BaselineAgent(BaseAgent):
    """
    Baseline single-turn agent that reads the files once, generates a single patch,
    applies it, and finishes without iterative self-repair. Useful for baseline benchmark calibration.
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

        await emit("agent_started", f"Starting BaselineAgent on task", {"model": self.provider.model_name})

        # List files
        files = await sandbox.list_files(".")
        await emit("tool_call", "Listing repository files", {"files": files})

        prompt = f"""Task: {task_prompt}
Files in repository: {files}
Constraints: {constraints or 'None'}

Provide the solution as a tool call to write_file.
"""
        messages = [
            LLMMessage(role="system", content="You are a single-pass coding agent. Analyze the request and call write_file to solve it."),
            LLMMessage(role="user", content=prompt)
        ]

        tools = ToolRegistry.get_tool_definitions()

        try:
            resp = await self.provider.generate(messages=messages, tools=tools, max_tokens=4096)
            tool_calls_count = 0
            if resp.tool_calls:
                for tc in resp.tool_calls:
                    tool_calls_count += 1
                    await emit("tool_call", f"Applying patch: {tc.name}", {"tool": tc.name, "arguments": tc.arguments})
                    await ToolRegistry.execute_tool(sandbox=sandbox, tool_name=tc.name, arguments=tc.arguments)

            git_diff = await sandbox.get_git_diff()
            await emit("agent_finished", "BaselineAgent completed single-pass execution.", {})

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
