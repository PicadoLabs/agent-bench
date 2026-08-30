from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel


class CommandResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


class BaseSandbox(ABC):
    """Abstract interface for benchmark execution sandboxes."""

    def __init__(self, workspace_path: str, run_id: str, timeout_seconds: int = 120):
        self.workspace_path = workspace_path
        self.run_id = run_id
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def start(self) -> None:
        """Initialize the sandbox environment and copy/mount repository files."""
        pass

    @abstractmethod
    async def execute_command(self, command: str, timeout_seconds: Optional[int] = None, env: Optional[Dict[str, str]] = None) -> CommandResult:
        """Execute a shell command inside the sandbox."""
        pass

    @abstractmethod
    async def read_file(self, relative_path: str) -> str:
        """Read a file from within the sandbox workspace."""
        pass

    @abstractmethod
    async def write_file(self, relative_path: str, content: str) -> None:
        """Write content to a file within the sandbox workspace."""
        pass

    @abstractmethod
    async def list_files(self, relative_path: str = ".") -> list[str]:
        """List files in the sandbox workspace."""
        pass

    @abstractmethod
    async def get_git_diff(self) -> str:
        """Get git diff of changes made inside the sandbox."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Tear down and clean up sandbox resources."""
        pass
