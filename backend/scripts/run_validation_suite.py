"""
Automated validation suite runner for AgentBench:
Runs all 10 original benchmarks across BaselineAgent, FastPatchAgent, and IterativeCodingAgent.
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.storage.database import init_db, SessionLocal
from app.benchmarks.loader import BenchmarkLoader
from app.benchmarks.runner import BenchmarkRunner
from app.config.settings import get_settings

BENCHMARK_IDS = [
    "fix-auth-jwt",
    "feat-fastapi-pagination",
    "fix-rate-limiter",
    "fix-sql-builder",
    "fix-lru-ttl-cache",
    "fix-csv-pipeline",
    "refactor-tree-serializer",
    "feat-config-loader",
    "debug-async-queue",
    "debug-markdown-parser"
]


async def main():
    settings = get_settings()
    init_db()
    db = SessionLocal()

    # Sync benchmarks
    tasks_dir = os.path.abspath(os.path.join(settings.benchmarks_dir, "tasks"))
    BenchmarkLoader.sync_benchmarks_to_db(db, tasks_dir)

    runner = BenchmarkRunner(db=db)

    print("=== Starting Comprehensive Validation Across 10 Benchmarks ===")

    # 1. Run all 10 tasks on IterativeCodingAgent with mock/local
    for b_id in BENCHMARK_IDS:
        print(f"\n---> Running Benchmark: {b_id} on IterativeCodingAgent...")
        try:
            run_data = await runner.execute_run(
                benchmark_id=b_id,
                agent_name="IterativeCodingAgent",
                model_name="mock-coder",
                provider_name="mock",
                sandbox_runtime="local"
            )
            score = run_data.get("score", 0)
            duration = run_data.get("metrics", {}).get("duration_seconds", 0)
            passed = run_data.get("passed_tests", 0)
            total = run_data.get("total_tests", 0)
            print(f"     Status: {run_data['status']} | Score: {score}/100 | Tests: {passed}/{total} | Duration: {duration}s")
        except Exception as e:
            print(f"     Error on {b_id}: {e}")

    # 2. Run selected tasks on BaselineAgent
    for b_id in ["fix-rate-limiter", "fix-sql-builder", "feat-config-loader"]:
        print(f"\n---> Running BaselineAgent on {b_id}...")
        try:
            run_data = await runner.execute_run(
                benchmark_id=b_id,
                agent_name="BaselineAgent",
                model_name="mock-coder",
                provider_name="mock",
                sandbox_runtime="local"
            )
            score = run_data.get("score", 0)
            passed = run_data.get("passed_tests", 0)
            total = run_data.get("total_tests", 0)
            print(f"     Status: {run_data['status']} | Score: {score}/100 | Tests: {passed}/{total}")
        except Exception as e:
            print(f"     Error on {b_id}: {e}")

    # 3. Run selected tasks on FastPatchAgent
    for b_id in ["fix-rate-limiter", "fix-sql-builder", "feat-fastapi-pagination"]:
        print(f"\n---> Running FastPatchAgent on {b_id}...")
        try:
            run_data = await runner.execute_run(
                benchmark_id=b_id,
                agent_name="FastPatchAgent",
                model_name="mock-coder",
                provider_name="mock",
                sandbox_runtime="local"
            )
            score = run_data.get("score", 0)
            passed = run_data.get("passed_tests", 0)
            total = run_data.get("total_tests", 0)
            print(f"     Status: {run_data['status']} | Score: {score}/100 | Tests: {passed}/{total}")
        except Exception as e:
            print(f"     Error on {b_id}: {e}")

    db.close()
    print("\n=======================================================")
    print("ALL VALIDATION RUNS COMPLETE AND SAVED TO SQLITE DATABASE")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(main())

