import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.storage.database import get_db
from app.storage.models import BenchmarkModel, TaskModel
from app.storage.repository import BenchmarkRepository
from app.benchmarks.loader import BenchmarkLoader
from app.config.settings import get_settings

router = APIRouter(prefix="/api/benchmarks", tags=["benchmarks"])


class CreateBenchmarkRequest(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    category: str = "Bug Fixing"
    difficulty: str = "Medium"
    repo_path: str
    repo_commit: str = "HEAD"
    prompt: str
    constraints: Optional[str] = ""
    evaluation_command: str = "pytest"
    evaluation_timeout: int = 120
    scoring_weights: Optional[Dict[str, float]] = None


@router.get("")
def list_benchmarks(db: Session = Depends(get_db)):
    """List all available benchmarks and tasks."""
    repo = BenchmarkRepository(db)
    benchmarks = repo.get_all()
    
    # If DB is empty, auto-sync from benchmarks/tasks directory
    if not benchmarks:
        settings = get_settings()
        BenchmarkLoader.sync_benchmarks_to_db(db, os.path.join(settings.benchmarks_dir, "tasks"))
        benchmarks = repo.get_all()

    results = []
    for b in benchmarks:
        t = b.tasks[0] if b.tasks else None
        results.append({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "category": b.category,
            "difficulty": b.difficulty,
            "repo_type": b.repo_type,
            "repo_path": b.repo_path,
            "repo_commit": b.repo_commit,
            "evaluation_command": t.evaluation_command if t else "pytest",
            "evaluation_timeout": t.evaluation_timeout if t else 120,
            "scoring_weights": t.scoring_weights if t else {},
            "prompt": t.prompt if t else "",
            "constraints": t.constraints if t else "",
            "total_runs": len(b.runs)
        })
    return results


@router.get("/{benchmark_id}")
def get_benchmark(benchmark_id: str, db: Session = Depends(get_db)):
    """Get single benchmark by ID."""
    repo = BenchmarkRepository(db)
    b = repo.get_by_id(benchmark_id)
    if not b:
        raise HTTPException(status_code=404, detail=f"Benchmark '{benchmark_id}' not found.")
    
    t = b.tasks[0] if b.tasks else None
    return {
        "id": b.id,
        "name": b.name,
        "description": b.description,
        "category": b.category,
        "difficulty": b.difficulty,
        "repo_type": b.repo_type,
        "repo_path": b.repo_path,
        "repo_commit": b.repo_commit,
        "evaluation_command": t.evaluation_command if t else "pytest",
        "evaluation_timeout": t.evaluation_timeout if t else 120,
        "scoring_weights": t.scoring_weights if t else {},
        "prompt": t.prompt if t else "",
        "constraints": t.constraints if t else "",
        "total_runs": len(b.runs)
    }


@router.post("")
def create_benchmark(payload: CreateBenchmarkRequest, db: Session = Depends(get_db)):
    """Create a new custom benchmark task."""
    repo = BenchmarkRepository(db)
    bench_data = {
        "id": payload.id,
        "name": payload.name,
        "description": payload.description,
        "category": payload.category,
        "difficulty": payload.difficulty,
        "repo_type": "local",
        "repo_path": payload.repo_path,
        "repo_commit": payload.repo_commit
    }
    task_data = {
        "id": f"{payload.id}-task",
        "prompt": payload.prompt,
        "constraints": payload.constraints,
        "evaluation_command": payload.evaluation_command,
        "evaluation_timeout": payload.evaluation_timeout,
        "scoring_weights": payload.scoring_weights or {
            "correctness": 50,
            "test_pass_rate": 25,
            "code_quality": 10,
            "efficiency": 10,
            "reliability": 5
        }
    }
    b = repo.create_or_update(bench_data, task_data)
    return {"status": "success", "id": b.id, "name": b.name}
