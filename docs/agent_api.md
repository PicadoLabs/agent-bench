# Agent API & Custom Agent Guide

AgentBench allows developers to evaluate custom coding agent architectures using a standard Python interface.

## Implementing a Custom Agent

Create a subclass of `BaseAgent` and implement the `run` method:

```python
from app.agents.base import BaseAgent, AgentRunResult, EventCallback
from app.sandbox.base import BaseSandbox
from app.agents.tools import ToolRegistry

class MyCustomCodingAgent(BaseAgent):
    async def run(
        self,
        task_prompt: str,
        sandbox: BaseSandbox,
        constraints: str = None,
        test_command: str = "pytest",
        on_event: EventCallback = None
    ) -> AgentRunResult:
        # 1. Read files using sandbox tools
        files = await sandbox.list_files(".")
        
        # 2. Inspect target source code
        source = await sandbox.read_file("auth_service.py")
        
        # 3. Apply surgical patch
        patched_code = source.replace("alg == 'none'", "False")
        await sandbox.write_file("auth_service.py", patched_code)
        
        # 4. Run tests
        res = await sandbox.execute_command(test_command)
        
        return AgentRunResult(
            success=(res.exit_code == 0),
            status="SUCCEEDED" if res.exit_code == 0 else "FAILED",
            total_steps=1,
            tool_calls_count=2,
            git_diff=await sandbox.get_git_diff()
        )
```

## Available Sandbox Tools

- `sandbox.read_file(path: str) -> str`
- `sandbox.write_file(path: str, content: str) -> None`
- `sandbox.list_files(path: str = ".") -> list[str]`
- `sandbox.execute_command(command: str, timeout_seconds: int = 120) -> CommandResult`
- `sandbox.get_git_diff() -> str`
- `sandbox.cleanup() -> None`

