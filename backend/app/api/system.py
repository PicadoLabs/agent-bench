import sys
import os
import httpx
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.storage.database import get_db
from app.storage.models import AgentRegistryModel, ModelRegistryModel, RunModel
from app.storage.repository import RunRepository
from app.config.settings import get_settings, PROVIDER_PRICING
from app.sandbox.factory import is_docker_available

router = APIRouter(prefix="/api", tags=["system"])


class CompareRequest(BaseModel):
    run_ids: List[str]


@router.get("/failures")
def get_failures(db: Session = Depends(get_db)):
    """Fetch failure taxonomy distribution and recent failures."""
    repo = RunRepository(db)
    return repo.get_failure_stats()


@router.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    """List registered agents and calculate their historical stats."""
    agents = db.query(AgentRegistryModel).all()
    runs = db.query(RunModel).all()

    results = []
    for a in agents:
        agent_runs = [r for r in runs if r.agent_name == a.name or r.agent_name == a.id]
        total_runs = len(agent_runs)
        succ = sum(1 for r in agent_runs if r.status == "SUCCEEDED")
        avg_sc = sum(r.total_score for r in agent_runs) / total_runs if total_runs > 0 else 0.0
        success_rate = (succ / total_runs) * 100.0 if total_runs > 0 else 0.0

        results.append({
            "id": a.id,
            "name": a.name,
            "agent_type": a.agent_type,
            "description": a.description,
            "version": a.version,
            "is_active": a.is_active,
            "total_runs": total_runs,
            "success_rate": round(success_rate, 1),
            "avg_score": round(avg_sc, 1)
        })
    return results


@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    """List registered LLM models, provider types, and cost rates."""
    models = db.query(ModelRegistryModel).all()
    runs = db.query(RunModel).all()

    results = []
    for m in models:
        model_runs = [r for r in runs if r.model_name == m.id or r.model_name == m.name]
        total_runs = len(model_runs)
        avg_sc = sum(r.total_score for r in model_runs) / total_runs if total_runs > 0 else 0.0
        avg_cost = sum(r.estimated_cost for r in model_runs) / total_runs if total_runs > 0 else 0.0

        results.append({
            "id": m.id,
            "name": m.name,
            "provider": m.provider,
            "is_local": m.is_local,
            "context_window": m.context_window,
            "pricing": m.pricing_metadata or {"input": 0.0, "output": 0.0},
            "total_runs": total_runs,
            "avg_score": round(avg_sc, 1),
            "avg_cost": round(avg_cost, 4)
        })
    return results


@router.get("/doctor")
async def system_doctor():
    """Diagnose system environment, Docker daemon, Ollama reachability, database, and API keys."""
    settings = get_settings()

    # Check Ollama
    ollama_ok = False
    ollama_models = []
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{settings.ollama_base_url}/api/tags")
            if res.status_code == 200:
                ollama_ok = True
                ollama_models = [m.get("name") for m in res.json().get("models", [])]
    except Exception:
        ollama_ok = False

    # Check Docker
    docker_ok = is_docker_available()

    # Check API keys
    api_keys = {
        "openai": bool(settings.openai_api_key),
        "anthropic": bool(settings.anthropic_api_key),
        "gemini": bool(settings.gemini_api_key),
        "custom": bool(settings.custom_api_key)
    }

    return {
        "status": "healthy",
        "python_version": sys.version.split()[0],
        "docker_available": docker_ok,
        "ollama_available": ollama_ok,
        "ollama_models": ollama_models,
        "default_provider": settings.model_provider,
        "default_model": settings.model_name,
        "sandbox_runtime": settings.sandbox_runtime,
        "configured_api_keys": api_keys,
        "database_url": settings.database_url
    }


@router.post("/compare")
def compare_runs(payload: CompareRequest, db: Session = Depends(get_db)):
    """Compare performance metrics, score breakdowns, and diffs across multiple runs."""
    repo = RunRepository(db)
    runs_data = []

    for r_id in payload.run_ids:
        r = repo.get_run(r_id)
        if r:
            score = r.score_breakdown
            runs_data.append({
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
                "git_diff": r.git_diff,
                "correctness": score.correctness if score else 0.0,
                "code_quality": score.code_quality if score else 0.0,
                "efficiency": score.efficiency if score else 0.0,
                "reliability": score.reliability if score else 0.0
            })

    return {"compared_runs": runs_data}
