import pytest
from app.scoring.engine import ScoringEngine


def test_perfect_score():
    score = ScoringEngine.calculate_score(
        passed_tests=20,
        total_tests=20,
        exit_code=0,
        duration_seconds=30.0,
        tool_calls_count=8,
        retries_count=0,
        status="SUCCEEDED",
        git_diff="--- a/auth.py\n+++ b/auth.py\n@@ -1 +1 @@\n- bad\n+ good"
    )
    assert score.overall_score >= 90.0
    assert score.correctness == 50.0
    assert score.test_pass_rate == 25.0
    assert score.code_quality >= 9.0
    assert score.efficiency == 10.0
    assert score.reliability == 5.0


def test_partial_score():
    score = ScoringEngine.calculate_score(
        passed_tests=10,
        total_tests=20,
        exit_code=1,
        duration_seconds=60.0,
        tool_calls_count=12,
        retries_count=2,
        status="PARTIAL",
        git_diff="diff"
    )
    assert 20.0 < score.overall_score < 75.0
    assert score.test_pass_rate == 12.5


def test_failed_score():
    score = ScoringEngine.calculate_score(
        passed_tests=0,
        total_tests=10,
        exit_code=1,
        duration_seconds=120.0,
        tool_calls_count=25,
        retries_count=3,
        status="FAILED",
        git_diff=""
    )
    assert score.overall_score < 30.0
    assert score.correctness == 0.0
    assert score.test_pass_rate == 0.0
