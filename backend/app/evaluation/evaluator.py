import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.sandbox.base import BaseSandbox, CommandResult
from app.evaluation.test_parser import TestOutputParser, ParsedTestOutput


class EvaluationOutcome(BaseModel):
    command: str
    exit_code: int
    duration_seconds: float
    parsed_results: ParsedTestOutput
    success: bool
    status: str  # SUCCEEDED, PARTIAL, FAILED, TIMEOUT


class ObjectiveEvaluator:
    """Runs automated test suites and static checks inside the sandbox post-agent execution."""

    @staticmethod
    async def evaluate_sandbox(
        sandbox: BaseSandbox,
        test_command: str = "pytest",
        timeout_seconds: int = 120
    ) -> EvaluationOutcome:
        start_t = time.time()
        cmd_result: CommandResult = await sandbox.execute_command(test_command, timeout_seconds=timeout_seconds)
        duration = time.time() - start_t

        parsed = TestOutputParser.parse_generic(test_command, cmd_result.stdout, cmd_result.stderr, cmd_result.exit_code)

        if cmd_result.timed_out:
            status = "TIMEOUT"
            success = False
        elif cmd_result.exit_code == 0 and parsed.failed == 0 and parsed.errors == 0:
            status = "SUCCEEDED"
            success = True
        elif parsed.passed > 0 and (parsed.failed > 0 or parsed.errors > 0):
            status = "PARTIAL"
            success = False
        else:
            status = "FAILED"
            success = False

        return EvaluationOutcome(
            command=test_command,
            exit_code=cmd_result.exit_code,
            duration_seconds=round(duration, 2),
            parsed_results=parsed,
            success=success,
            status=status
        )
