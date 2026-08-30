from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import datetime
from app.storage.models import (
    BenchmarkModel,
    TaskModel,
    RunModel,
    ToolCallModel,
    ExecutionEventModel,
    TestResultModel,
    ScoreModel,
    FailureAnalysisModel,
    AgentRegistryModel,
    ModelRegistryModel
)


class BenchmarkRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[BenchmarkModel]:
        return self.db.query(BenchmarkModel).order_by(BenchmarkModel.name).all()

    def get_by_id(self, benchmark_id: str) -> Optional[BenchmarkModel]:
        return self.db.query(BenchmarkModel).filter(BenchmarkModel.id == benchmark_id).first()

    def create_or_update(self, benchmark_data: Dict[str, Any], task_data: Optional[Dict[str, Any]] = None) -> BenchmarkModel:
        bench_id = benchmark_data["id"]
        benchmark = self.get_by_id(bench_id)
        if not benchmark:
            benchmark = BenchmarkModel(**benchmark_data)
            self.db.add(benchmark)
        else:
            for k, v in benchmark_data.items():
                setattr(benchmark, k, v)
        
        self.db.flush()

        if task_data:
            task_copy = dict(task_data)
            task_id = task_copy.pop("id", f"{bench_id}-task")
            task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
            if not task:
                task = TaskModel(id=task_id, benchmark_id=bench_id, **task_copy)
                self.db.add(task)
            else:
                for k, v in task_copy.items():
                    setattr(task, k, v)

        self.db.commit()
        self.db.refresh(benchmark)
        return benchmark


class RunRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_run_id(self) -> str:
        count = self.db.query(RunModel).count() + 1
        return f"RUN-{count:04d}"

    def create_run(self, run_id: str, benchmark_id: str, benchmark_name: str, agent_name: str, model_name: str, provider_name: str, config_snapshot: Dict[str, Any] = None) -> RunModel:
        run = RunModel(
            id=run_id,
            benchmark_id=benchmark_id,
            benchmark_name=benchmark_name,
            agent_name=agent_name,
            model_name=model_name,
            provider_name=provider_name,
            status="QUEUED",
            start_time=datetime.datetime.utcnow(),
            config_snapshot=config_snapshot or {}
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_run(self, run_id: str) -> Optional[RunModel]:
        return self.db.query(RunModel).filter(RunModel.id == run_id).first()

    def list_runs(self, limit: int = 50, offset: int = 0, benchmark_id: Optional[str] = None, agent_name: Optional[str] = None, model_name: Optional[str] = None) -> List[RunModel]:
        query = self.db.query(RunModel)
        if benchmark_id:
            query = query.filter(RunModel.benchmark_id == benchmark_id)
        if agent_name:
            query = query.filter(RunModel.agent_name == agent_name)
        if model_name:
            query = query.filter(RunModel.model_name == model_name)
        return query.order_by(desc(RunModel.start_time)).offset(offset).limit(limit).all()

    def update_run_status(self, run_id: str, status: str, **kwargs) -> Optional[RunModel]:
        run = self.get_run(run_id)
        if run:
            run.status = status
            for k, v in kwargs.items():
                if hasattr(run, k):
                    setattr(run, k, v)
            self.db.commit()
            self.db.refresh(run)
        return run

    def add_event(self, run_id: str, event_type: str, message: str, step_number: int = 0, details: Dict[str, Any] = None) -> ExecutionEventModel:
        event = ExecutionEventModel(
            run_id=run_id,
            event_type=event_type,
            step_number=step_number,
            message=message,
            details=details or {},
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(event)
        self.db.commit()
        return event

    def add_tool_call(self, run_id: str, step_number: int, tool_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any], duration_seconds: float = 0.0, error: Optional[str] = None) -> ToolCallModel:
        tool_call = ToolCallModel(
            run_id=run_id,
            step_number=step_number,
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            duration_seconds=duration_seconds,
            error=error,
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(tool_call)
        self.db.commit()
        return tool_call

    def save_test_result(self, run_id: str, phase: str, command: str, exit_code: int, duration_seconds: float, passed: int, failed: int, skipped: int, total: int, stdout: str, stderr: str, details: Dict[str, Any] = None) -> TestResultModel:
        result = TestResultModel(
            run_id=run_id,
            phase=phase,
            command=command,
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            passed_count=passed,
            failed_count=failed,
            skipped_count=skipped,
            total_count=total,
            stdout=stdout,
            stderr=stderr,
            test_details=details or {},
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(result)
        self.db.commit()
        return result

    def save_score(self, run_id: str, correctness: float, test_pass_rate: float, code_quality: float, efficiency: float, reliability: float, overall_score: float, breakdown: Dict[str, Any], ai_judge: Optional[Dict[str, Any]] = None) -> ScoreModel:
        score = ScoreModel(
            run_id=run_id,
            correctness=correctness,
            test_pass_rate=test_pass_rate,
            code_quality=code_quality,
            efficiency=efficiency,
            reliability=reliability,
            overall_score=overall_score,
            breakdown=breakdown,
            ai_judge_evaluation=ai_judge,
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(score)
        self.db.commit()
        return score

    def save_failure_analysis(self, run_id: str, primary_failure: str, root_cause: str, failed_tests: int = 0, attempts: int = 1, resolution_hints: str = "", details: Dict[str, Any] = None) -> FailureAnalysisModel:
        analysis = FailureAnalysisModel(
            run_id=run_id,
            primary_failure=primary_failure,
            root_cause=root_cause,
            failed_tests_count=failed_tests,
            attempts_count=attempts,
            resolution_hints=resolution_hints,
            details=details or {},
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(analysis)
        self.db.commit()
        return analysis

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        # Aggregated leaderboard by agent & model
        runs = self.db.query(RunModel).filter(RunModel.status.in_(["SUCCEEDED", "PARTIAL", "FAILED", "TIMEOUT", "CRASHED"])).all()
        
        groups: Dict[str, List[RunModel]] = {}
        for r in runs:
            key = f"{r.agent_name}::{r.model_name}::{r.provider_name}"
            if key not in groups:
                groups[key] = []
            groups[key].append(r)

        leaderboard = []
        for key, run_list in groups.items():
            agent_name, model_name, provider_name = key.split("::")
            total_runs = len(run_list)
            successful_runs = sum(1 for r in run_list if r.status == "SUCCEEDED")
            avg_score = sum(r.total_score for r in run_list) / total_runs if total_runs > 0 else 0.0
            avg_time = sum(r.duration_seconds for r in run_list) / total_runs if total_runs > 0 else 0.0
            avg_cost = sum(r.estimated_cost for r in run_list) / total_runs if total_runs > 0 else 0.0
            avg_tool_calls = sum(r.tool_calls_count for r in run_list) / total_runs if total_runs > 0 else 0.0
            success_rate = (successful_runs / total_runs) * 100.0 if total_runs > 0 else 0.0

            leaderboard.append({
                "agent_name": agent_name,
                "model_name": model_name,
                "provider_name": provider_name,
                "total_runs": total_runs,
                "success_rate": round(success_rate, 1),
                "avg_score": round(avg_score, 1),
                "avg_time": round(avg_time, 1),
                "avg_cost": round(avg_cost, 4),
                "avg_tool_calls": round(avg_tool_calls, 1),
                "is_local": provider_name in ["ollama", "local", "mock"]
            })

        leaderboard.sort(key=lambda x: (x["avg_score"], x["success_rate"]), reverse=True)
        for idx, item in enumerate(leaderboard):
            item["rank"] = idx + 1
        return leaderboard

    def get_failure_stats(self) -> Dict[str, Any]:
        analyses = self.db.query(FailureAnalysisModel).all()
        categories: Dict[str, int] = {}
        items = []

        for a in analyses:
            categories[a.primary_failure] = categories.get(a.primary_failure, 0) + 1
            items.append({
                "run_id": a.run_id,
                "primary_failure": a.primary_failure,
                "root_cause": a.root_cause,
                "failed_tests_count": a.failed_tests_count,
                "attempts_count": a.attempts_count,
                "resolution_hints": a.resolution_hints,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None
            })

        return {
            "category_counts": categories,
            "total_failures": len(analyses),
            "recent_failures": items[-20:]
        }
