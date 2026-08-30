from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ScoreResult(BaseModel):
    correctness: float
    test_pass_rate: float
    code_quality: float
    efficiency: float
    reliability: float
    overall_score: float
    breakdown: Dict[str, Any] = Field(default_factory=dict)


class ScoringEngine:
    """
    Computes weighted benchmark score (0-100) based on objective test results,
    agent execution metrics, retry count, and code patch quality.
    """

    @staticmethod
    def calculate_score(
        passed_tests: int,
        total_tests: int,
        exit_code: int,
        duration_seconds: float,
        tool_calls_count: int,
        retries_count: int,
        status: str,
        git_diff: str = "",
        weights: Optional[Dict[str, float]] = None,
        ai_judge_quality: Optional[float] = None
    ) -> ScoreResult:
        w = weights or {
            "correctness": 50.0,
            "test_pass_rate": 25.0,
            "code_quality": 10.0,
            "efficiency": 10.0,
            "reliability": 5.0
        }

        # 1. Test Pass Rate (0.0 to 1.0)
        pass_ratio = (passed_tests / total_tests) if total_tests > 0 else (1.0 if exit_code == 0 else 0.0)
        score_test_pass = pass_ratio * w.get("test_pass_rate", 25.0)

        # 2. Correctness (0.0 to 1.0)
        if status == "SUCCEEDED" and exit_code == 0 and pass_ratio >= 1.0:
            correctness_ratio = 1.0
        elif pass_ratio > 0.0:
            correctness_ratio = pass_ratio * 0.7  # Partial solution
        else:
            correctness_ratio = 0.0
        score_correctness = correctness_ratio * w.get("correctness", 50.0)

        # 3. Code Quality (0.0 to 1.0)
        # Based on diff presence, minimal line changes, and optional AI judge rating
        diff_lines = len([l for l in git_diff.splitlines() if l.startswith("+") or l.startswith("-")]) if git_diff else 0
        if ai_judge_quality is not None:
            quality_ratio = min(1.0, max(0.0, ai_judge_quality / 10.0))
        elif diff_lines > 0 and diff_lines < 150:
            quality_ratio = 0.95  # Surgical, concise patch
        elif diff_lines >= 150:
            quality_ratio = 0.70  # Large patch
        else:
            quality_ratio = 0.50 if status == "SUCCEEDED" else 0.20
        score_quality = quality_ratio * w.get("code_quality", 10.0)

        # 4. Efficiency (0.0 to 1.0)
        # Penalize excessive tool calls (>15) or long durations (>90s)
        eff_ratio = 1.0
        if tool_calls_count > 15:
            eff_ratio -= min(0.4, (tool_calls_count - 15) * 0.03)
        if duration_seconds > 90.0:
            eff_ratio -= min(0.3, (duration_seconds - 90.0) * 0.005)
        eff_ratio = max(0.1, eff_ratio)
        score_efficiency = eff_ratio * w.get("efficiency", 10.0)

        # 5. Reliability (0.0 to 1.0)
        # Penalized by retries and non-clean statuses
        rel_ratio = 1.0
        if status in ["TIMEOUT", "CRASHED"]:
            rel_ratio = 0.0
        elif status == "FAILED":
            rel_ratio = 0.2
        else:
            rel_ratio -= min(0.5, retries_count * 0.15)
        rel_ratio = max(0.0, rel_ratio)
        score_reliability = rel_ratio * w.get("reliability", 5.0)

        # Normalize total score to 0 - 100
        overall = score_correctness + score_test_pass + score_quality + score_efficiency + score_reliability
        overall = round(max(0.0, min(100.0, overall)), 1)

        breakdown = {
            "correctness": round(score_correctness, 1),
            "test_pass_rate": round(score_test_pass, 1),
            "code_quality": round(score_quality, 1),
            "efficiency": round(score_efficiency, 1),
            "reliability": round(score_reliability, 1),
            "weights": w
        }

        return ScoreResult(
            correctness=round(score_correctness, 1),
            test_pass_rate=round(score_test_pass, 1),
            code_quality=round(score_quality, 1),
            efficiency=round(score_efficiency, 1),
            reliability=round(score_reliability, 1),
            overall_score=overall,
            breakdown=breakdown
        )
