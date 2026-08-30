import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.storage.models import Base
from app.storage.database import init_db
from app.benchmarks.loader import BenchmarkLoader
from app.benchmarks.runner import BenchmarkRunner
from app.providers.mock_provider import MockProvider
from app.providers.base import LLMResponse, ToolCall


CORRECT_SQL_BUILDER_CODE = """# query_builder.py - Fixed Parameterized SQL Query Builder
from typing import List, Dict, Any, Tuple, Optional


class QueryBuilder:
    def __init__(self, table: str):
        self.table = table
        self.selected_columns: List[str] = ["*"]
        self.where_conditions: List[Tuple[str, str, Any]] = []
        self.order_by_col: Optional[str] = None
        self.order_dir: str = "ASC"
        self.limit_val: Optional[int] = None

    def select(self, *columns: str) -> "QueryBuilder":
        if columns:
            self.selected_columns = list(columns)
        return self

    def where(self, column: str, operator: str, value: Any) -> "QueryBuilder":
        self.where_conditions.append((column, operator, value))
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self.order_by_col = column
        self.order_dir = direction.upper() if direction.upper() in ["ASC", "DESC"] else "ASC"
        return self

    def limit(self, count: int) -> "QueryBuilder":
        if count < 0:
            raise ValueError("Limit must be non-negative")
        self.limit_val = count
        return self

    def build(self) -> Tuple[str, List[Any]]:
        cols = ", ".join(self.selected_columns)
        sql = f"SELECT {cols} FROM {self.table}"
        params: List[Any] = []

        if self.where_conditions:
            where_parts = []
            for col, op, val in self.where_conditions:
                where_parts.append(f"{col} {op} ?")
                params.append(val)
            sql += " WHERE " + " AND ".join(where_parts)

        if self.order_by_col:
            sql += f" ORDER BY {self.order_by_col} {self.order_dir}"

        if self.limit_val is not None:
            sql += f" LIMIT {self.limit_val}"

        return sql, params
"""


@pytest.mark.asyncio
async def test_full_benchmark_run_lifecycle_e2e():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 1. Sync tasks
        BenchmarkLoader.sync_benchmarks_to_db(db, "./benchmarks/tasks")

        # 2. Setup scripted agent responses: write fixed query_builder.py, run tests
        script = [
            LLMResponse(
                content="Applying fix to query_builder.py to parameterize SQL queries.",
                tool_calls=[
                    ToolCall(
                        name="write_file",
                        arguments={"path": "query_builder.py", "content": CORRECT_SQL_BUILDER_CODE}
                    )
                ],
                input_tokens=200,
                output_tokens=100,
                provider_name="mock"
            ),
            LLMResponse(
                content="Running tests to verify.",
                tool_calls=[
                    ToolCall(
                        name="run_tests",
                        arguments={"command": "pytest test_query_builder.py"}
                    )
                ],
                input_tokens=100,
                output_tokens=50,
                provider_name="mock"
            ),
            LLMResponse(
                content="All tests pass successfully.",
                tool_calls=[],
                input_tokens=50,
                output_tokens=20,
                provider_name="mock"
            )
        ]

        # Patch factory to return this mock provider
        from unittest.mock import patch
        mock_prov = MockProvider(model_name="mock-coder", script=script)

        with patch("app.benchmarks.runner.get_provider", return_value=mock_prov):
            runner = BenchmarkRunner(db)
            result = await runner.execute_run(
                benchmark_id="fix-sql-builder",
                agent_name="IterativeCodingAgent",
                model_name="mock-coder",
                provider_name="mock"
            )

        assert result["status"] == "SUCCEEDED"
        assert result["score"] >= 85.0
        assert result["passed_tests"] > 0
        assert result["failure_analysis"] is None
        assert result["metrics"]["total_tokens"] > 0
        assert len(result["git_diff"]) > 0

    finally:
        db.close()
