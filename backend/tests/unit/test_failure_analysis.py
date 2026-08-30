import pytest
from app.failure_analysis.analyzer import FailureAnalyzer


def test_syntax_error_classification():
    stdout = "File 'auth.py', line 12\n    def func(\n            ^\nSyntaxError: unexpected EOF while parsing"
    res = FailureAnalyzer.analyze(
        status="FAILED",
        exit_code=1,
        stdout=stdout,
        stderr="",
        failed_tests_count=1,
        retries_count=0
    )
    assert res.primary_failure == "syntax_error"
    assert "SyntaxError" in res.root_cause


def test_timeout_classification():
    res = FailureAnalyzer.analyze(
        status="TIMEOUT",
        exit_code=-1,
        stdout="",
        stderr="Execution timed out",
        failed_tests_count=0,
        retries_count=1
    )
    assert res.primary_failure == "timeout"


def test_test_failure_classification():
    stdout = "FAILED test_auth.py::test_tampered_payload - AssertionError: assert False is True"
    res = FailureAnalyzer.analyze(
        status="FAILED",
        exit_code=1,
        stdout=stdout,
        stderr="",
        failed_tests_count=2,
        retries_count=2,
        git_diff="modified diff"
    )
    assert res.primary_failure == "test_failure"
    assert res.failed_tests_count == 2
