import os
import shutil
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.sandbox.base import BaseSandbox, CommandResult


class SecurityError(Exception):
    pass


class LocalSandbox(BaseSandbox):
    """
    Subprocess-based sandbox with strict path traversal prevention, isolated workspace directory,
    and sanitized environment variables. Ideal for fast local development and environments without Docker.
    """

    def __init__(self, workspace_path: str, run_id: str, timeout_seconds: int = 120):
        super().__init__(workspace_path, run_id, timeout_seconds)
        self.root_path = Path(os.path.abspath(workspace_path)).resolve()

    def _resolve_safe_path(self, relative_path: str) -> Path:
        """Ensure path is within the designated workspace root to prevent path traversal."""
        # Normalize and resolve
        clean_rel = relative_path.lstrip("/\\")
        target = (self.root_path / clean_rel).resolve()
        
        # Check that target starts with root_path
        try:
            target.relative_to(self.root_path)
        except ValueError:
            raise SecurityError(f"Path traversal attempt blocked: '{relative_path}' escapes workspace '{self.root_path}'")
        return target

    async def start(self) -> None:
        self.root_path.mkdir(parents=True, exist_ok=True)

    async def read_file(self, relative_path: str) -> str:
        target = self._resolve_safe_path(relative_path)
        if not target.exists():
            raise FileNotFoundError(f"File not found in sandbox: {relative_path}")
        if not target.is_file():
            raise IsADirectoryError(f"Path is a directory, not a file: {relative_path}")
        return target.read_text(encoding="utf-8", errors="replace")

    async def write_file(self, relative_path: str, content: str) -> None:
        target = self._resolve_safe_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    async def list_files(self, relative_path: str = ".") -> List[str]:
        target = self._resolve_safe_path(relative_path)
        if not target.exists():
            return []
        
        file_list = []
        for root, dirs, files in os.walk(target):
            # Ignore .git, __pycache__, .pytest_cache
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", ".pytest_cache", "venv", ".venv"]]
            for f in files:
                full = Path(root) / f
                try:
                    rel = full.relative_to(self.root_path)
                    file_list.append(str(rel).replace("\\", "/"))
                except ValueError:
                    continue
        return sorted(file_list)

    async def execute_command(self, command: str, timeout_seconds: Optional[int] = None, env: Optional[Dict[str, str]] = None) -> CommandResult:
        timeout = timeout_seconds or self.timeout_seconds
        start_t = time.time()
        
        # Clean environment: preserve system runtime environment but strip secrets/API keys
        safe_env = dict(os.environ)
        # Strip sensitive API keys so they never leak to sandbox agents
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "CUSTOM_API_KEY"]:
            safe_env.pop(key, None)

        safe_env["PYTHONPATH"] = str(self.root_path)
        safe_env["PYTHONUNBUFFERED"] = "1"
        if env:
            safe_env.update(env)

        # Normalize pytest commands on Windows to python -m pytest if needed
        cmd_to_run = command
        if cmd_to_run.startswith("pytest"):
            cmd_to_run = f"python -m {cmd_to_run}"

        # Run process asynchronously in the workspace cwd
        try:
            process = await asyncio.create_subprocess_shell(
                cmd_to_run,
                cwd=str(self.root_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=safe_env
            )
            
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
                duration = time.time() - start_t
                return CommandResult(
                    command=command,
                    exit_code=process.returncode if process.returncode is not None else 1,
                    stdout=stdout_bytes.decode("utf-8", errors="replace"),
                    stderr=stderr_bytes.decode("utf-8", errors="replace"),
                    duration_seconds=round(duration, 2),
                    timed_out=False
                )
            except asyncio.TimeoutError:
                # Terminate process tree
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
                duration = time.time() - start_t
                return CommandResult(
                    command=command,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Command execution timed out after {timeout} seconds.",
                    duration_seconds=round(duration, 2),
                    timed_out=True
                )
        except Exception as e:
            duration = time.time() - start_t
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Failed to execute command: {str(e)}",
                duration_seconds=round(duration, 2),
                timed_out=False
            )

    async def get_git_diff(self) -> str:
        # Check if git is initialized
        git_dir = self.root_path / ".git"
        if git_dir.exists():
            res = await self.execute_command("git diff")
            return res.stdout
        return ""

    async def cleanup(self) -> None:
        """Clean up workspace directory if needed."""
        try:
            if self.root_path.exists():
                shutil.rmtree(self.root_path, ignore_errors=True)
        except Exception:
            pass
