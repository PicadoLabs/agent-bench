import os
import shutil
import time
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Awaitable
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.benchmarks.schema import BenchmarkTaskYAML
from app.benchmarks.loader import BenchmarkLoader
from app.providers.factory import get_provider
from app.sandbox.factory import get_sandbox
from app.agents.factory import get_agent
from app.evaluation.evaluator import ObjectiveEvaluator, EvaluationOutcome
from app.evaluation.llm_judge import LLMJudge
from app.scoring.engine import ScoringEngine
from app.metrics.collector import MetricsCollector
from app.failure_analysis.analyzer import FailureAnalyzer
from app.storage.repository import RunRepository, BenchmarkRepository

# Live event callback for WebSocket broadcasting: async (event_data: dict) -> None
EventBroadcaster = Optional[Callable[[Dict[str, Any]], Awaitable[None]]]


class BenchmarkRunner:
    """
    Core orchestrator that runs end-to-end benchmark tasks:
    Sandbox -> Agent Loop -> Objective Evaluation -> Scoring -> Failure Taxonomy -> Persistence.
    """

    def __init__(self, db: Session):
        self.db = db
        self.run_repo = RunRepository(db)
        self.settings = get_settings()

    async def execute_run(
        self,
        benchmark_id: str,
        agent_name: str = "IterativeCodingAgent",
        model_name: Optional[str] = None,
        provider_name: Optional[str] = None,
        run_id: Optional[str] = None,
        sandbox_runtime: Optional[str] = None,
        enable_llm_judge: bool = False,
        broadcaster: EventBroadcaster = None
    ) -> Dict[str, Any]:
        
        # 1. Load benchmark & task
        bench_repo = BenchmarkRepository(self.db)
        benchmark_db = bench_repo.get_by_id(benchmark_id)
        
        if not benchmark_db:
            # Try to load and sync from task YAML
            task_file = Path(self.settings.benchmarks_dir) / "tasks" / f"{benchmark_id}.yaml"
            if not task_file.exists():
                # search by name/id
                for f in (Path(self.settings.benchmarks_dir) / "tasks").glob("*.yaml"):
                    task_yaml = BenchmarkLoader.load_from_yaml(str(f))
                    if task_yaml.id == benchmark_id:
                        task_file = f
                        break
            
            if task_file.exists():
                BenchmarkLoader.sync_benchmarks_to_db(self.db, str(task_file.parent))
                benchmark_db = bench_repo.get_by_id(benchmark_id)

        if not benchmark_db or not benchmark_db.tasks:
            raise ValueError(f"Benchmark '{benchmark_id}' not found or has no tasks configured.")

        task_db = benchmark_db.tasks[0]
        actual_run_id = run_id or self.run_repo.generate_run_id()
        actual_model = model_name or self.settings.model_name
        actual_provider = provider_name or self.settings.model_provider

        # 2. Register run in DB (State: PREPARING)
        run_record = self.run_repo.create_run(
            run_id=actual_run_id,
            benchmark_id=benchmark_id,
            benchmark_name=benchmark_db.name,
            agent_name=agent_name,
            model_name=actual_model,
            provider_name=actual_provider,
            config_snapshot={
                "benchmark_id": benchmark_id,
                "category": benchmark_db.category,
                "difficulty": benchmark_db.difficulty,
                "sandbox_runtime": sandbox_runtime or self.settings.sandbox_runtime,
                "evaluation_command": task_db.evaluation_command,
                "scoring_weights": task_db.scoring_weights
            }
        )

        async def emit_event(event_type: str, message: str, details: Dict[str, Any] = None):
            det = details or {}
            event_obj = self.run_repo.add_event(
                run_id=actual_run_id,
                event_type=event_type,
                message=message,
                step_number=det.get("step", 0),
                details=det
            )
            if broadcaster:
                try:
                    await broadcaster({
                        "run_id": actual_run_id,
                        "event_type": event_type,
                        "message": message,
                        "step_number": det.get("step", 0),
                        "details": det,
                        "timestamp": event_obj.timestamp.isoformat()
                    })
                except Exception:
                    pass

        await emit_event("benchmark_started", f"Benchmark {benchmark_db.name} ({actual_run_id}) initiated.")

        # 3. Setup isolated sandbox workspace
        workspace_dir = Path(self.settings.workspaces_dir) / actual_run_id
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Copy repository files into workspace
        source_repo_path = Path(benchmark_db.repo_path)
        if not source_repo_path.is_absolute():
            source_repo_path = (Path.cwd() / source_repo_path).resolve()

        if source_repo_path.exists():
            for item in source_repo_path.iterdir():
                dest = workspace_dir / item.name
                if item.is_dir():
                    if item.name not in [".git", "__pycache__", ".pytest_cache"]:
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        # Initialize local git repository in workspace for diff tracking
        try:
            import subprocess
            subprocess.run(["git", "init"], cwd=str(workspace_dir), capture_output=True, check=False)
            subprocess.run(["git", "config", "user.name", "AgentBench"], cwd=str(workspace_dir), capture_output=True, check=False)
            subprocess.run(["git", "config", "user.email", "agent@agentbench.local"], cwd=str(workspace_dir), capture_output=True, check=False)
            subprocess.run(["git", "add", "-A"], cwd=str(workspace_dir), capture_output=True, check=False)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(workspace_dir), capture_output=True, check=False)
        except Exception:
            pass
        
        await emit_event("repository_prepared", f"Repository {source_repo_path.name} loaded into sandbox.", {"path": str(workspace_dir)})

        # 4. Instantiate Sandbox
        sandbox = get_sandbox(
            workspace_path=str(workspace_dir),
            run_id=actual_run_id,
            runtime=sandbox_runtime,
            timeout_seconds=task_db.evaluation_timeout
        )
        await sandbox.start()
        await emit_event("sandbox_created", "Isolated sandbox container initialized.", {"runtime": type(sandbox).__name__})

        # 5. Instantiate Provider and Agent
        provider = get_provider(provider_name=actual_provider, model_name=actual_model)
        agent = get_agent(
            agent_name=agent_name,
            provider=provider,
            max_steps=self.settings.max_agent_steps,
            max_retries=self.settings.max_retries
        )

        start_time = time.time()
        self.run_repo.update_run_status(actual_run_id, "RUNNING")
        await emit_event("agent_started", f"Agent {agent_name} started execution.", {"model": actual_model, "provider": actual_provider})

        # Agent execution event dispatcher
        async def on_agent_event(event_type: str, msg: str, details: Dict[str, Any]):
            await emit_event(event_type, msg, details)
            if event_type == "tool_result":
                self.run_repo.add_tool_call(
                    run_id=actual_run_id,
                    step_number=details.get("step", 0),
                    tool_name=details.get("tool", "unknown"),
                    input_data=details.get("arguments", {}),
                    output_data=details.get("output", {}),
                    duration_seconds=details.get("duration", 0.0),
                    error=details.get("error")
                )

        # 6. Execute Agent Loop
        try:
            agent_result = await agent.run(
                task_prompt=task_db.prompt,
                sandbox=sandbox,
                constraints=task_db.constraints,
                test_command=task_db.evaluation_command,
                on_event=on_agent_event
            )
        except Exception as e:
            agent_result = None
            await emit_event("agent_crashed", f"Agent crashed unexpectedly: {str(e)}", {"error": str(e)})

        # 7. Post-execution Objective Evaluation
        self.run_repo.update_run_status(actual_run_id, "TESTING")
        await emit_event("test_started", f"Executing evaluation test command: {task_db.evaluation_command}")

        eval_outcome: EvaluationOutcome = await ObjectiveEvaluator.evaluate_sandbox(
            sandbox=sandbox,
            test_command=task_db.evaluation_command,
            timeout_seconds=task_db.evaluation_timeout
        )

        await emit_event("test_finished", f"Test evaluation completed. Passed: {eval_outcome.parsed_results.passed}/{eval_outcome.parsed_results.total}", {
            "exit_code": eval_outcome.exit_code,
            "passed": eval_outcome.parsed_results.passed,
            "failed": eval_outcome.parsed_results.failed,
            "total": eval_outcome.parsed_results.total
        })

        # Save test result record
        self.run_repo.save_test_result(
            run_id=actual_run_id,
            phase="final_evaluation",
            command=eval_outcome.command,
            exit_code=eval_outcome.exit_code,
            duration_seconds=eval_outcome.duration_seconds,
            passed=eval_outcome.parsed_results.passed,
            failed=eval_outcome.parsed_results.failed,
            skipped=eval_outcome.parsed_results.skipped,
            total=eval_outcome.parsed_results.total,
            stdout=eval_outcome.parsed_results.raw_stdout,
            stderr=eval_outcome.parsed_results.raw_stderr,
            details={"failures": eval_outcome.parsed_results.failures_summary}
        )

        # 8. Inspect Git Diff
        git_diff = await sandbox.get_git_diff()
        if not git_diff and agent_result and agent_result.git_diff:
            git_diff = agent_result.git_diff

        # 9. Optional AI Judge Evaluation
        ai_judge_data = None
        if enable_llm_judge:
            self.run_repo.update_run_status(actual_run_id, "EVALUATING")
            await emit_event("evaluation_started", "Running AI-Assisted LLM Judge evaluation.")
            judge = LLMJudge(provider=provider)
            judge_res = await judge.evaluate(
                task_prompt=task_db.prompt,
                git_diff=git_diff,
                test_summary=f"{eval_outcome.parsed_results.passed}/{eval_outcome.parsed_results.total} passed",
                agent_output=agent_result.final_output if agent_result else ""
            )
            ai_judge_data = judge_res.model_dump()
            await emit_event("evaluation_finished", "AI-Assisted LLM Judge evaluation complete.", ai_judge_data)

        # 10. Compute Metrics & Scoring
        total_duration = time.time() - start_time
        tool_calls_cnt = agent_result.tool_calls_count if agent_result else 0
        retries_cnt = agent_result.retries_count if agent_result else 0
        in_tokens = agent_result.input_tokens if agent_result else 0
        out_tokens = agent_result.output_tokens if agent_result else 0

        # Classify Final Status
        if eval_outcome.status == "SUCCEEDED" and eval_outcome.parsed_results.failed == 0:
            final_status = "SUCCEEDED"
        elif eval_outcome.status == "PARTIAL" or (eval_outcome.parsed_results.passed > 0):
            final_status = "PARTIAL"
        elif eval_outcome.status == "TIMEOUT":
            final_status = "TIMEOUT"
        elif agent_result and agent_result.status == "CRASHED":
            final_status = "CRASHED"
        else:
            final_status = "FAILED"

        score_res = ScoringEngine.calculate_score(
            passed_tests=eval_outcome.parsed_results.passed,
            total_tests=eval_outcome.parsed_results.total,
            exit_code=eval_outcome.exit_code,
            duration_seconds=total_duration,
            tool_calls_count=tool_calls_cnt,
            retries_count=retries_cnt,
            status=final_status,
            git_diff=git_diff,
            weights=task_db.scoring_weights,
            ai_judge_quality=ai_judge_data.get("code_quality_rating") if ai_judge_data else None
        )

        metrics = MetricsCollector.compute_metrics(
            duration_seconds=total_duration,
            tool_calls_count=tool_calls_cnt,
            commands_count=tool_calls_cnt,
            retries_count=retries_cnt,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            passed_tests=eval_outcome.parsed_results.passed,
            failed_tests=eval_outcome.parsed_results.failed,
            total_tests=eval_outcome.parsed_results.total,
            provider_name=actual_provider,
            model_name=actual_model
        )

        # 11. Failure Taxonomy Analysis
        failure_res = FailureAnalyzer.analyze(
            status=final_status,
            exit_code=eval_outcome.exit_code,
            stdout=eval_outcome.parsed_results.raw_stdout,
            stderr=eval_outcome.parsed_results.raw_stderr,
            failed_tests_count=eval_outcome.parsed_results.failed,
            retries_count=retries_cnt,
            error_message=agent_result.error_message if agent_result else None,
            git_diff=git_diff
        )

        # 12. Save all results & update run status in DB
        self.run_repo.save_score(
            run_id=actual_run_id,
            correctness=score_res.correctness,
            test_pass_rate=score_res.test_pass_rate,
            code_quality=score_res.code_quality,
            efficiency=score_res.efficiency,
            reliability=score_res.reliability,
            overall_score=score_res.overall_score,
            breakdown=score_res.breakdown,
            ai_judge=ai_judge_data
        )

        if final_status != "SUCCEEDED":
            self.run_repo.save_failure_analysis(
                run_id=actual_run_id,
                primary_failure=failure_res.primary_failure,
                root_cause=failure_res.root_cause,
                failed_tests=failure_res.failed_tests_count,
                attempts=failure_res.attempts_count,
                resolution_hints=failure_res.resolution_hints,
                details=failure_res.details
            )

        self.run_repo.update_run_status(
            actual_run_id,
            status=final_status,
            end_time=datetime.datetime.utcnow(),
            duration_seconds=round(total_duration, 2),
            total_score=score_res.overall_score,
            test_pass_rate=metrics.test_pass_rate,
            passed_tests=eval_outcome.parsed_results.passed,
            failed_tests=eval_outcome.parsed_results.failed,
            total_tests=eval_outcome.parsed_results.total,
            tool_calls_count=tool_calls_cnt,
            commands_count=tool_calls_cnt,
            retries_count=retries_cnt,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            total_tokens=metrics.total_tokens,
            estimated_cost=metrics.estimated_cost,
            git_diff=git_diff,
            logs=eval_outcome.parsed_results.raw_stdout
        )

        await emit_event(
            "benchmark_completed" if final_status == "SUCCEEDED" else "benchmark_failed",
            f"Run {actual_run_id} finished with status: {final_status} and score {score_res.overall_score}/100.",
            {
                "status": final_status,
                "score": score_res.overall_score,
                "duration": round(total_duration, 2),
                "passed_tests": eval_outcome.parsed_results.passed,
                "total_tests": eval_outcome.parsed_results.total
            }
        )

        # 13. Sandbox Cleanup
        await sandbox.cleanup()

        return {
            "run_id": actual_run_id,
            "status": final_status,
            "score": score_res.overall_score,
            "score_breakdown": score_res.breakdown,
            "metrics": metrics.model_dump(),
            "passed_tests": eval_outcome.parsed_results.passed,
            "total_tests": eval_outcome.parsed_results.total,
            "git_diff": git_diff,
            "failure_analysis": failure_res.model_dump() if final_status != "SUCCEEDED" else None
        }
