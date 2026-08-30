import time
import re
from typing import Dict, Any, List, Optional, Callable, Awaitable
from pydantic import BaseModel
from app.providers.base import ToolDefinition
from app.sandbox.base import BaseSandbox


class ToolExecutionResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    duration_seconds: float
    error: Optional[str] = None
    success: bool = True


class ToolRegistry:
    """Registry of sandbox-bound tools available to benchmark agents."""

    @staticmethod
    def get_tool_definitions() -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="read_file",
                description="Read the text content of a file in the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path of the file to read."}
                    },
                    "required": ["path"]
                }
            ),
            ToolDefinition(
                name="write_file",
                description="Write or overwrite full text content to a file in the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path of the file to write."},
                        "content": {"type": "string", "description": "The exact content to write into the file."}
                    },
                    "required": ["path", "content"]
                }
            ),
            ToolDefinition(
                name="list_files",
                description="List all files and subdirectories in the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative directory path. Defaults to '.' (root)."}
                    }
                }
            ),
            ToolDefinition(
                name="search_files",
                description="Search for a regex or string pattern across files in the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search pattern or substring."},
                        "path": {"type": "string", "description": "Relative directory or file to search within."}
                    },
                    "required": ["query"]
                }
            ),
            ToolDefinition(
                name="run_command",
                description="Execute an arbitrary shell command in the workspace.",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command line to execute."}
                    },
                    "required": ["command"]
                }
            ),
            ToolDefinition(
                name="run_tests",
                description="Run the repository test suite (e.g., pytest, npm test).",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Test command to execute. Defaults to pytest."}
                    }
                }
            ),
            ToolDefinition(
                name="git_diff",
                description="Inspect the current git diff of changes made in the workspace.",
                parameters={
                    "type": "object",
                    "properties": {}
                }
            ),
            ToolDefinition(
                name="git_status",
                description="Check modified, untracked, or staged files via git status.",
                parameters={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

    @staticmethod
    async def execute_tool(sandbox: BaseSandbox, tool_name: str, arguments: Dict[str, Any]) -> ToolExecutionResult:
        start_t = time.time()
        try:
            if tool_name == "read_file":
                path = arguments.get("path", "")
                content = await sandbox.read_file(path)
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    output={"content": content, "lines": len(content.splitlines())},
                    duration_seconds=round(duration, 3),
                    success=True
                )

            elif tool_name == "write_file":
                path = arguments.get("path", "")
                content = arguments.get("content", "")
                await sandbox.write_file(path, content)
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments={"path": path, "bytes_written": len(content.encode("utf-8"))},
                    output={"status": "success", "message": f"Successfully wrote {len(content)} characters to {path}"},
                    duration_seconds=round(duration, 3),
                    success=True
                )

            elif tool_name == "list_files":
                path = arguments.get("path", ".")
                files = await sandbox.list_files(path)
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    output={"files": files, "count": len(files)},
                    duration_seconds=round(duration, 3),
                    success=True
                )

            elif tool_name == "search_files":
                query = arguments.get("query", "")
                all_files = await sandbox.list_files(".")
                matches = []
                for f in all_files:
                    try:
                        content = await sandbox.read_file(f)
                        for line_no, line in enumerate(content.splitlines(), start=1):
                            if re.search(query, line, re.IGNORECASE):
                                matches.append({"file": f, "line_number": line_no, "line": line.strip()})
                                if len(matches) >= 50:
                                    break
                    except Exception:
                        continue
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    output={"matches": matches, "count": len(matches)},
                    duration_seconds=round(duration, 3),
                    success=True
                )

            elif tool_name == "run_command":
                cmd = arguments.get("command", "")
                res = await sandbox.execute_command(cmd)
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    output={
                        "exit_code": res.exit_code,
                        "stdout": res.stdout,
                        "stderr": res.stderr,
                        "timed_out": res.timed_out
                    },
                    duration_seconds=round(duration, 3),
                    success=(res.exit_code == 0)
                )

            elif tool_name == "run_tests":
                cmd = arguments.get("command", "pytest")
                res = await sandbox.execute_command(cmd)
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    output={
                        "exit_code": res.exit_code,
                        "stdout": res.stdout,
                        "stderr": res.stderr,
                        "passed": "passed" in res.stdout.lower() and res.exit_code == 0
                    },
                    duration_seconds=round(duration, 3),
                    success=(res.exit_code == 0)
                )

            elif tool_name == "git_diff":
                diff = await sandbox.get_git_diff()
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments={},
                    output={"diff": diff},
                    duration_seconds=round(duration, 3),
                    success=True
                )

            elif tool_name == "git_status":
                res = await sandbox.execute_command("git status --short")
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments={},
                    output={"status": res.stdout},
                    duration_seconds=round(duration, 3),
                    success=True
                )

            else:
                duration = time.time() - start_t
                return ToolExecutionResult(
                    tool_name=tool_name,
                    arguments=arguments,
                    output=None,
                    duration_seconds=round(duration, 3),
                    error=f"Unknown tool: '{tool_name}'",
                    success=False
                )

        except Exception as e:
            duration = time.time() - start_t
            return ToolExecutionResult(
                tool_name=tool_name,
                arguments=arguments,
                output=None,
                duration_seconds=round(duration, 3),
                error=str(e),
                success=False
            )
