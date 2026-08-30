import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent, AgentRunResult, EventCallback
from app.agents.tools import ToolRegistry, ToolExecutionResult
from app.providers.base import LLMMessage, ToolCall
from app.sandbox.base import BaseSandbox

SYSTEM_PROMPT = """You are a senior AI software engineering agent evaluated by AgentBench.
Your goal is to inspect the codebase in the isolated workspace, understand the task requirements and constraints, investigate bugs or missing features, apply surgical code changes using provided tools, and verify that all tests pass.

Rules and Strategy:
1. First, explore the directory structure and read relevant source files and tests.
2. Formulate a precise hypothesis of the issue.
3. Make clean, minimal, surgical code modifications using write_file. Do not rewrite unrelated files.
4. Run tests with run_tests or run_command to check whether your modifications pass the test suite.
5. If tests fail, read the test failure output carefully, fix the issue, and re-run tests.
6. When all tests pass and the task is solved, provide a brief summary of the changes and conclude.
"""


class IterativeCodingAgent(BaseAgent):
    """
    Standard Iterative ReAct Coding Agent.
    Performs multi-step exploration, surgical file edits, automated test execution,
    and iterative repair loops upon test failures.
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

        await emit("agent_started", f"Starting {self.name} on task", {"model": self.provider.model_name})

        # Build initial messages
        user_prompt = f"Task Description:\n{task_prompt}\n"
        if constraints:
            user_prompt += f"\nConstraints:\n{constraints}\n"
        user_prompt += f"\nEvaluation Test Command: {test_command}\n"

        messages: List[LLMMessage] = [
            LLMMessage(role="system", content=SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt)
        ]

        tools = ToolRegistry.get_tool_definitions()

        total_input_tokens = 0
        total_output_tokens = 0
        total_tool_calls = 0
        retries_count = 0
        step = 0
        final_output = ""

        try:
            while step < self.max_steps:
                step += 1
                await emit("agent_step", f"Step {step}/{self.max_steps}: Consulting model {self.provider.model_name}", {"step": step})

                # Call model
                try:
                    response = await self.provider.generate(
                        messages=messages,
                        tools=tools,
                        temperature=0.2,
                        max_tokens=4096
                    )
                except Exception as e:
                    await emit("agent_error", f"Model generation error: {str(e)}", {"error": str(e)})
                    return AgentRunResult(
                        success=False,
                        status="CRASHED",
                        total_steps=step,
                        tool_calls_count=total_tool_calls,
                        retries_count=retries_count,
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        total_tokens=total_input_tokens + total_output_tokens,
                        final_output="",
                        error_message=f"Model generation failed: {str(e)}",
                        git_diff=await sandbox.get_git_diff()
                    )

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                if response.content:
                    final_output = response.content

                # If no tool calls, model finished its reasoning
                if not response.tool_calls:
                    await emit("agent_finished", f"Agent concluded task execution after {step} steps.", {"summary": response.content})
                    break

                # Add assistant message with tool calls
                messages.append(LLMMessage(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls
                ))

                # Execute each tool call
                for tc in response.tool_calls:
                    total_tool_calls += 1
                    await emit("tool_call", f"Tool call: {tc.name}", {
                        "tool": tc.name,
                        "arguments": tc.arguments,
                        "step": step
                    })

                    tool_res: ToolExecutionResult = await ToolRegistry.execute_tool(
                        sandbox=sandbox,
                        tool_name=tc.name,
                        arguments=tc.arguments
                    )

                    await emit("tool_result", f"Tool {tc.name} completed in {tool_res.duration_seconds}s", {
                        "tool": tc.name,
                        "success": tool_res.success,
                        "duration": tool_res.duration_seconds,
                        "output": tool_res.output,
                        "error": tool_res.error
                    })

                    # Handle retry tracking on test runs
                    if tc.name in ["run_tests", "run_command"]:
                        cmd_out = tool_res.output or {}
                        if isinstance(cmd_out, dict) and cmd_out.get("exit_code", 0) != 0:
                            retries_count += 1
                            await emit("retry_started", f"Tests failed. Triggering repair iteration #{retries_count}", {
                                "retries": retries_count,
                                "exit_code": cmd_out.get("exit_code")
                            })

                    # Format tool result for conversation history
                    res_str = json.dumps(tool_res.output) if tool_res.output is not None else f"Error: {tool_res.error}"
                    messages.append(LLMMessage(
                        role="tool",
                        content=res_str,
                        tool_call_id=tc.id or tc.name
                    ))

            git_diff = await sandbox.get_git_diff()
            status = "SUCCEEDED" if total_tool_calls > 0 else "PARTIAL"

            return AgentRunResult(
                success=True,
                status=status,
                total_steps=step,
                tool_calls_count=total_tool_calls,
                retries_count=retries_count,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                total_tokens=total_input_tokens + total_output_tokens,
                final_output=final_output,
                git_diff=git_diff
            )

        except Exception as e:
            await emit("agent_error", f"Agent execution crashed: {str(e)}", {"error": str(e)})
            return AgentRunResult(
                success=False,
                status="CRASHED",
                total_steps=step,
                tool_calls_count=total_tool_calls,
                retries_count=retries_count,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                total_tokens=total_input_tokens + total_output_tokens,
                final_output="",
                error_message=str(e),
                git_diff=await sandbox.get_git_diff()
            )
