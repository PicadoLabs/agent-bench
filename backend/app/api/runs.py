import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.storage.database import get_db, SessionLocal
from app.storage.models import RunModel
from app.storage.repository import RunRepository
from app.benchmarks.runner import BenchmarkRunner
from app.api.websocket import ws_manager

router = APIRouter(prefix="/api/runs", tags=["runs"])


class StartRunRequest(BaseModel):
    benchmark_id: str
    agent_name: str = "IterativeCodingAgent"
    model_name: Optional[str] = None
    provider_name: Optional[str] = None
    sandbox_runtime: Optional[str] = None
    enable_llm_judge: bool = False


async def run_benchmark_in_background(run_id: str, payload: StartRunRequest):
    """Background execution task with live WebSocket event streaming."""
    db = SessionLocal()
    try:
        runner = BenchmarkRunner(db)
        
        async def broadcast_event(event_dict: Dict[str, Any]):
            await ws_manager.broadcast_event(run_id, event_dict)

        await runner.execute_run(
            benchmark_id=payload.benchmark_id,
            agent_name=payload.agent_name,
            model_name=payload.model_name,
            provider_name=payload.provider_name,
            run_id=run_id,
            sandbox_runtime=payload.sandbox_runtime,
            enable_llm_judge=payload.enable_llm_judge,
            broadcaster=broadcast_event
        )
    except Exception as e:
        print(f"[RunBackground] Error running {run_id}: {e}")
    finally:
        db.close()


@router.post("")
async def start_run(payload: StartRunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Initiates an asynchronous benchmark run and returns the run_id."""
    repo = RunRepository(db)
    run_id = repo.generate_run_id()

    # Launch in background
    background_tasks.add_task(run_benchmark_in_background, run_id, payload)

    return {
        "status": "QUEUED",
        "run_id": run_id,
        "benchmark_id": payload.benchmark_id,
        "agent_name": payload.agent_name,
        "message": f"Run {run_id} has been queued for execution."
    }


@router.get("")
def list_runs(
    limit: int = 50,
    offset: int = 0,
    benchmark_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    model_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List runs with optional filtering."""
    repo = RunRepository(db)
    runs = repo.list_runs(limit=limit, offset=offset, benchmark_id=benchmark_id, agent_name=agent_name, model_name=model_name)
    
    return [
        {
            "id": r.id,
            "benchmark_id": r.benchmark_id,
            "benchmark_name": r.benchmark_name,
            "agent_name": r.agent_name,
            "model_name": r.model_name,
            "provider_name": r.provider_name,
            "status": r.status,
            "total_score": r.total_score,
            "test_pass_rate": r.test_pass_rate,
            "passed_tests": r.passed_tests,
            "failed_tests": r.failed_tests,
            "total_tests": r.total_tests,
            "duration_seconds": r.duration_seconds,
            "tool_calls_count": r.tool_calls_count,
            "retries_count": r.retries_count,
            "estimated_cost": r.estimated_cost,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "end_time": r.end_time.isoformat() if r.end_time else None
        }
        for r in runs
    ]


@router.get("/{run_id}")
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    """Fetch complete run details, including events, tool calls, tests, score breakdown, and failure analysis."""
    repo = RunRepository(db)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    score = run.score_breakdown
    failure = run.failure_analysis

    return {
        "id": run.id,
        "benchmark_id": run.benchmark_id,
        "benchmark_name": run.benchmark_name,
        "agent_name": run.agent_name,
        "model_name": run.model_name,
        "provider_name": run.provider_name,
        "status": run.status,
        "start_time": run.start_time.isoformat() if run.start_time else None,
        "end_time": run.end_time.isoformat() if run.end_time else None,
        "duration_seconds": run.duration_seconds,
        "total_score": run.total_score,
        "test_pass_rate": run.test_pass_rate,
        "passed_tests": run.passed_tests,
        "failed_tests": run.failed_tests,
        "total_tests": run.total_tests,
        "tool_calls_count": run.tool_calls_count,
        "commands_count": run.commands_count,
        "retries_count": run.retries_count,
        "input_tokens": run.input_tokens,
        "output_tokens": run.output_tokens,
        "total_tokens": run.total_tokens,
        "estimated_cost": run.estimated_cost,
        "git_diff": run.git_diff,
        "logs": run.logs,
        "score_breakdown": {
            "correctness": score.correctness if score else 0.0,
            "test_pass_rate": score.test_pass_rate if score else 0.0,
            "code_quality": score.code_quality if score else 0.0,
            "efficiency": score.efficiency if score else 0.0,
            "reliability": score.reliability if score else 0.0,
            "overall_score": score.overall_score if score else 0.0,
            "breakdown": score.breakdown if score else {},
            "ai_judge_evaluation": score.ai_judge_evaluation if score else None
        } if score else None,
        "failure_analysis": {
            "primary_failure": failure.primary_failure,
            "root_cause": failure.root_cause,
            "failed_tests_count": failure.failed_tests_count,
            "attempts_count": failure.attempts_count,
            "resolution_hints": failure.resolution_hints,
            "details": failure.details
        } if failure else None,
        "tool_calls": [
            {
                "step": tc.step_number,
                "tool": tc.tool_name,
                "input": tc.input_data,
                "output": tc.output_data,
                "duration": tc.duration_seconds,
                "error": tc.error,
                "timestamp": tc.timestamp.isoformat() if tc.timestamp else None
            }
            for tc in run.tool_calls
        ],
        "events": [
            {
                "event_type": ev.event_type,
                "step": ev.step_number,
                "message": ev.message,
                "details": ev.details,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None
            }
            for ev in run.execution_events
        ],
        "test_results": [
            {
                "command": tr.command,
                "exit_code": tr.exit_code,
                "duration": tr.duration_seconds,
                "passed": tr.passed_count,
                "failed": tr.failed_count,
                "skipped": tr.skipped_count,
                "total": tr.total_count,
                "stdout": tr.stdout,
                "stderr": tr.stderr,
                "details": tr.test_details
            }
            for tr in run.test_results
        ]
    }


@router.get("/{run_id}/diff")
def get_run_diff(run_id: str, db: Session = Depends(get_db)):
    repo = RunRepository(db)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return {"run_id": run.id, "git_diff": run.git_diff or ""}


@router.get("/{run_id}/events")
def get_run_events(run_id: str, db: Session = Depends(get_db)):
    repo = RunRepository(db)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return [
        {
            "event_type": ev.event_type,
            "step": ev.step_number,
            "message": ev.message,
            "details": ev.details,
            "timestamp": ev.timestamp.isoformat() if ev.timestamp else None
        }
        for ev in run.execution_events
    ]


@router.websocket("/ws/{run_id}")
async def websocket_run_stream(websocket: WebSocket, run_id: str):
    """WebSocket connection endpoint for live run telemetry streaming."""
    await ws_manager.connect(run_id, websocket)
    try:
        while True:
            # Keep socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(run_id, websocket)
    except Exception:
        ws_manager.disconnect(run_id, websocket)
