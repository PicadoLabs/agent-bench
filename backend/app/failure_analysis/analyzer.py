import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class FailureAnalysisResult(BaseModel):
    primary_failure: str
    root_cause: str
    failed_tests_count: int
    attempts_count: int
    resolution_hints: str
    details: Dict[str, Any]


class FailureAnalyzer:
    """
    Automated taxonomy classifier and root-cause analyzer for failed or partial benchmark runs.
    """

    @staticmethod
    def analyze(
        status: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        failed_tests_count: int,
        retries_count: int,
        error_message: Optional[str] = None,
        tool_errors: Optional[List[str]] = None,
        git_diff: str = ""
    ) -> FailureAnalysisResult:
        combined_output = f"{stdout}\n{stderr}\n{error_message or ''}".lower()
        tool_errs = tool_errors or []

        # 1. Timeout Check
        if status == "TIMEOUT" or "timed out" in combined_output:
            return FailureAnalysisResult(
                primary_failure="timeout",
                root_cause="Execution exceeded designated sandbox time limit.",
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints="Optimize agent iteration steps or check for infinite loops / hanging subprocesses.",
                details={"status": status, "exit_code": exit_code}
            )

        # 2. Syntax Error Check
        if "syntaxerror" in combined_output or "indentationerror" in combined_output:
            match = re.search(r"(SyntaxError|IndentationError): (.*)", f"{stdout}\n{stderr}")
            cause_detail = match.group(0) if match else "Syntax error detected in patched file."
            return FailureAnalysisResult(
                primary_failure="syntax_error",
                root_cause=cause_detail,
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints="Agent introduced invalid Python syntax. Ensure proper indentation and matching quotes/parentheses.",
                details={"syntax_error": cause_detail}
            )

        # 3. Tool Misuse or Permission Error Check
        if any("blocked" in err.lower() or "escapes" in err.lower() for err in tool_errs) or "permissionerror" in combined_output:
            return FailureAnalysisResult(
                primary_failure="permission_error" if "permissionerror" in combined_output else "tool_misuse",
                root_cause="Agent attempted path traversal or illegal file access outside workspace boundary.",
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints="Constrain agent tool parameters to relative workspace paths.",
                details={"tool_errors": tool_errs}
            )

        # 4. Dependency Issue
        if "modulenotfounderror" in combined_output or "importerror" in combined_output:
            match = re.search(r"No module named '([^']+)'", f"{stdout}\n{stderr}")
            mod_name = match.group(1) if match else "unknown package"
            return FailureAnalysisResult(
                primary_failure="dependency_issue",
                root_cause=f"Missing module dependency: '{mod_name}'.",
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints=f"Ensure '{mod_name}' is installed in sandbox environment or imported correctly.",
                details={"missing_module": mod_name}
            )

        # 5. Test Failure (tests executed but assertions failed)
        if failed_tests_count > 0 or "assertionerror" in combined_output:
            # Extract first assertion error if available
            assert_match = re.search(r"AssertionError:? (.*)", f"{stdout}\n{stderr}")
            cause = assert_match.group(0) if assert_match else f"{failed_tests_count} unit tests failed assertion checks."
            return FailureAnalysisResult(
                primary_failure="test_failure",
                root_cause=cause,
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints="Review test assertions and ensure all edge-cases are handled in the patch.",
                details={"failed_tests": failed_tests_count}
            )

        # 6. Incomplete Solution (no file changes made or empty diff)
        if not git_diff.strip() and status != "SUCCEEDED":
            return FailureAnalysisResult(
                primary_failure="incomplete_solution",
                root_cause="Agent completed execution without applying any file modifications or git patches.",
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints="Verify prompt clarity and ensure agent invokes write_file to apply fixes.",
                details={"git_diff_length": 0}
            )

        # 7. Command Failure
        if exit_code != 0:
            return FailureAnalysisResult(
                primary_failure="command_failure",
                root_cause=f"Test command exited with non-zero status code: {exit_code}.",
                failed_tests_count=failed_tests_count,
                attempts_count=retries_count + 1,
                resolution_hints="Check stdout/stderr logs for unhandled exceptions or configuration problems.",
                details={"exit_code": exit_code}
            )

        # 8. Wrong Solution / Fallback
        return FailureAnalysisResult(
            primary_failure="wrong_solution" if status != "SUCCEEDED" else "none",
            root_cause="Code was modified but does not fulfill expected benchmark criteria." if status != "SUCCEEDED" else "Benchmark succeeded without failure.",
            failed_tests_count=failed_tests_count,
            attempts_count=retries_count + 1,
            resolution_hints="Review benchmark problem prompt and test requirements.",
            details={}
        )
