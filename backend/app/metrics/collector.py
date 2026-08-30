from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config.settings import PROVIDER_PRICING


class RunMetrics(BaseModel):
    duration_seconds: float = 0.0
    tool_calls_count: int = 0
    commands_count: int = 0
    retries_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    test_pass_rate: float = 0.0
    passed_tests: int = 0
    failed_tests: int = 0
    total_tests: int = 0


class MetricsCollector:
    @staticmethod
    def compute_metrics(
        duration_seconds: float,
        tool_calls_count: int,
        commands_count: int,
        retries_count: int,
        input_tokens: int,
        output_tokens: int,
        passed_tests: int,
        failed_tests: int,
        total_tests: int,
        provider_name: str,
        model_name: str
    ) -> RunMetrics:
        # Calculate cost
        pricing = None
        p_clean = provider_name.lower()
        if p_clean in PROVIDER_PRICING:
            p_dict = PROVIDER_PRICING[p_clean]
            if model_name in p_dict:
                pricing = p_dict[model_name]
            else:
                pricing = p_dict.get("default", {"input": 0.0, "output": 0.0})

        estimated_cost = 0.0
        if pricing:
            in_rate = pricing.get("input", 0.0) / 1_000_000.0
            out_rate = pricing.get("output", 0.0) / 1_000_000.0
            estimated_cost = round((input_tokens * in_rate) + (output_tokens * out_rate), 4)

        pass_rate = round((passed_tests / total_tests) * 100.0, 1) if total_tests > 0 else 0.0

        return RunMetrics(
            duration_seconds=round(duration_seconds, 2),
            tool_calls_count=tool_calls_count,
            commands_count=commands_count,
            retries_count=retries_count,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost=estimated_cost,
            test_pass_rate=pass_rate,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_tests=total_tests
        )
