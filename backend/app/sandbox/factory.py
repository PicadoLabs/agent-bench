import os
from typing import Optional
from app.config.settings import get_settings
from app.sandbox.base import BaseSandbox
from app.sandbox.local_sandbox import LocalSandbox
from app.sandbox.docker_sandbox import DockerSandbox


def is_docker_available() -> bool:
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def get_sandbox(
    workspace_path: str,
    run_id: str,
    runtime: Optional[str] = None,
    timeout_seconds: Optional[int] = None
) -> BaseSandbox:
    settings = get_settings()
    rt = (runtime or settings.sandbox_runtime).lower().strip()
    timeout = timeout_seconds or settings.default_timeout_seconds

    if rt == "docker":
        if is_docker_available():
            return DockerSandbox(
                workspace_path=workspace_path,
                run_id=run_id,
                image=settings.docker_image,
                timeout_seconds=timeout
            )
        else:
            # Safe graceful fallback with log
            print(f"[Sandbox] Docker requested for {run_id}, but Docker daemon is unreachable. Falling back to LocalSandbox.")
            return LocalSandbox(
                workspace_path=workspace_path,
                run_id=run_id,
                timeout_seconds=timeout
            )
    else:
        return LocalSandbox(
            workspace_path=workspace_path,
            run_id=run_id,
            timeout_seconds=timeout
        )
