import os
import shutil
import pytest
from pathlib import Path
from app.sandbox.local_sandbox import LocalSandbox, SecurityError


@pytest.mark.asyncio
async def test_local_sandbox_file_io():
    ws_dir = "./sandbox_workspaces/test_ws"
    sandbox = LocalSandbox(workspace_path=ws_dir, run_id="TEST-001")
    await sandbox.start()

    try:
        # Write file
        await sandbox.write_file("hello.txt", "Hello AgentBench!")
        
        # Read file
        content = await sandbox.read_file("hello.txt")
        assert content == "Hello AgentBench!"

        # List files
        files = await sandbox.list_files(".")
        assert "hello.txt" in files

        # Execute command
        res = await sandbox.execute_command("python -c \"print('Sandbox active')\"")
        assert res.exit_code == 0
        assert "Sandbox active" in res.stdout
    finally:
        await sandbox.cleanup()


@pytest.mark.asyncio
async def test_path_traversal_blocking():
    ws_dir = "./sandbox_workspaces/test_sec_ws"
    sandbox = LocalSandbox(workspace_path=ws_dir, run_id="TEST-SEC")
    await sandbox.start()

    try:
        with pytest.raises(SecurityError):
            await sandbox.read_file("../../etc/passwd")

        with pytest.raises(SecurityError):
            await sandbox.write_file("../malicious.sh", "echo bad")
    finally:
        await sandbox.cleanup()
