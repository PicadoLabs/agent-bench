import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ParsedTestOutput(BaseModel):
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total: int = 0
    pass_rate: float = 0.0
    failures_summary: List[str] = []
    raw_stdout: str = ""
    raw_stderr: str = ""


class TestOutputParser:
    @staticmethod
    def parse_pytest(stdout: str, stderr: str, exit_code: int) -> ParsedTestOutput:
        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        # Look for pytest summary line like: "=== 3 passed in 0.12s ===" or "=== 2 failed, 1 passed in 0.20s ==="
        summary_match = re.search(r"=+\s*(.*?)\s+in\s+[\d\.]+s\s*=+", stdout)
        if summary_match:
            summary_text = summary_match.group(1)
            p_match = re.search(r"(\d+)\s+passed", summary_text)
            if p_match:
                passed = int(p_match.group(1))

            f_match = re.search(r"(\d+)\s+failed", summary_text)
            if f_match:
                failed = int(f_match.group(1))

            s_match = re.search(r"(\d+)\s+skipped", summary_text)
            if s_match:
                skipped = int(s_match.group(1))

            e_match = re.search(r"(\d+)\s+error", summary_text)
            if e_match:
                errors = int(e_match.group(1))
        else:
            # Fallback regex for individual indicators: "1 passed", "2 failed"
            p_match = re.search(r"(\d+)\s+passed", stdout)
            if p_match:
                passed = int(p_match.group(1))
            f_match = re.search(r"(\d+)\s+failed", stdout)
            if f_match:
                failed = int(f_match.group(1))
            s_match = re.search(r"(\d+)\s+skipped", stdout)
            if s_match:
                skipped = int(s_match.group(1))
            e_match = re.search(r"(\d+)\s+error", stdout)
            if e_match:
                errors = int(e_match.group(1))

        # Extract failed test names
        failures = []
        for line in stdout.splitlines():
            if line.startswith("FAILED ") or line.startswith("ERROR "):
                failures.append(line.strip())

        total = passed + failed + errors + skipped
        if total == 0 and exit_code == 0 and ("passed" in stdout.lower() or "ok" in stdout.lower()):
            # Safe single test pass assumption if exit_code is 0 and output indicates ok
            passed = 1
            total = 1
        elif total == 0 and exit_code != 0:
            failed = 1
            total = 1

        pass_rate = round((passed / total) * 100.0, 2) if total > 0 else 0.0

        return ParsedTestOutput(
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total=total,
            pass_rate=pass_rate,
            failures_summary=failures,
            raw_stdout=stdout,
            raw_stderr=stderr
        )

    @staticmethod
    def parse_generic(command: str, stdout: str, stderr: str, exit_code: int) -> ParsedTestOutput:
        if "pytest" in command:
            return TestOutputParser.parse_pytest(stdout, stderr, exit_code)
        
        # Generic test fallback
        if exit_code == 0:
            return ParsedTestOutput(
                passed=1,
                failed=0,
                total=1,
                pass_rate=100.0,
                raw_stdout=stdout,
                raw_stderr=stderr
            )
        else:
            return ParsedTestOutput(
                passed=0,
                failed=1,
                total=1,
                pass_rate=0.0,
                failures_summary=[stderr.strip() or stdout.strip()],
                raw_stdout=stdout,
                raw_stderr=stderr
            )
