import os
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import docker
from docker.errors import DockerException, NotFound
from app.sandbox.base import BaseSandbox, CommandResult


class DockerSandbox(BaseSandbox):
    """
    Production-grade Docker sandbox for local agent benchmarking.
    Runs commands inside a clean, isolated container with mounted workspace,
    isolated network (or limited network), and automatic cleanup.
    """

    def __init__(
        self,
        workspace_path: str,
        run_id: str,
        image: str = "python:3.11-slim",
        timeout_seconds: int = 120,
        network_disabled: bool = True
    ):
        super().__init__(workspace_path, run_id, timeout_seconds)
        self.image = image
        self.network_disabled = network_disabled
        self.client: Optional[docker.DockerClient] = None
        self.container = None
        self.container_name = f"agentbench-run-{run_id.lower().replace('_', '-')}"
        self.root_path = Path(os.path.abspath(workspace_path)).resolve()

    def _get_client(self) -> docker.DockerClient:
        if not self.client:
            self.client = docker.from_env()
        return self.client

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sync_start)

    def _sync_start(self) -> None:
        client = self._get_client()
        self.root_path.mkdir(parents=True, exist_ok=True)
        
        # Remove any existing container with the same name
        try:
            old = client.containers.get(self.container_name)
            old.remove(force=True)
        except NotFound:
            pass

        # Start long-running idle container
        # Mount host workspace to /workspace
        volumes = {
            str(self.root_path): {
                "bind": "/workspace",
                "mode": "rw"
            }
        }

        self.container = client.containers.run(
            self.image,
            command="tail -f /dev/null",
            name=self.container_name,
            detach=True,
            working_dir="/workspace",
            volumes=volumes,
            network_disabled=self.network_disabled,
            mem_limit="2g",
            cpu_quota=100000,
            remove=False
        )

    async def execute_command(self, command: str, timeout_seconds: Optional[int] = None, env: Optional[Dict[str, str]] = None) -> CommandResult:
        timeout = timeout_seconds or self.timeout_seconds
        loop = asyncio.get_running_loop()
        start_t = time.time()

        def _exec():
            if not self.container:
                raise RuntimeError("Docker container not started.")
            
            exec_env = {
                "PYTHONUNBUFFERED": "1",
                "PYTHONPATH": "/workspace"
            }
            if env:
                exec_env.update(env)

            exec_instance = self.container.client.api.exec_create(
                self.container.id,
                cmd=["/bin/sh", "-c", command],
                workdir="/workspace",
                environment=exec_env
            )
            output = self.container.client.api.exec_start(exec_instance["Id"], stream=False, demux=True)
            inspect = self.container.client.api.exec_inspect(exec_instance["Id"])
            exit_code = inspect.get("ExitCode", 0)
            
            stdout_bytes, stderr_bytes = output if isinstance(output, tuple) else (output, b"")
            stdout_str = (stdout_bytes or b"").decode("utf-8", errors="replace")
            stderr_str = (stderr_bytes or b"").decode("utf-8", errors="replace")
            return exit_code, stdout_str, stderr_str

        try:
            exit_code, stdout, stderr = await asyncio.wait_for(
                loop.run_in_executor(None, _exec),
                timeout=timeout
            )
            duration = time.time() - start_t
            return CommandResult(
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=round(duration, 2),
                timed_out=False
            )
        except asyncio.TimeoutError:
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
                stderr=f"Docker exec error: {str(e)}",
                duration_seconds=round(duration, 2),
                timed_out=False
            )

    async def read_file(self, relative_path: str) -> str:
        # Files are mounted locally, so read from mounted root_path safely
        clean_rel = relative_path.lstrip("/\\")
        target = (self.root_path / clean_rel).resolve()
        target.relative_to(self.root_path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return target.read_text(encoding="utf-8", errors="replace")

    async def write_file(self, relative_path: str, content: str) -> None:
        clean_rel = relative_path.lstrip("/\\")
        target = (self.root_path / clean_rel).resolve()
        target.relative_to(self.root_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    async def list_files(self, relative_path: str = ".") -> List[str]:
        file_list = []
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", ".pytest_cache", "venv", ".venv"]]
            for f in files:
                full = Path(root) / f
                try:
                    rel = full.relative_to(self.root_path)
                    file_list.append(str(rel).replace("\\", "/"))
                except ValueError:
                    continue
        return sorted(file_list)

    async def get_git_diff(self) -> str:
        res = await self.execute_command("git diff")
        return res.stdout

    async def cleanup(self) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sync_cleanup)

    def _sync_cleanup(self) -> None:
        if self.container:
            try:
                self.container.stop(timeout=2)
                self.container.remove(force=True)
            except Exception:
                pass
            self.container = None
