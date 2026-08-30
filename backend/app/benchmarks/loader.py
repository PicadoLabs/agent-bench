import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.benchmarks.schema import BenchmarkTaskYAML
from app.storage.repository import BenchmarkRepository


class BenchmarkLoader:
    @staticmethod
    def load_from_yaml(yaml_path: str) -> BenchmarkTaskYAML:
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Benchmark task YAML not found at: {yaml_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        return BenchmarkTaskYAML(**data)

    @staticmethod
    def load_all_benchmarks(tasks_dir: str = "./benchmarks/tasks") -> List[BenchmarkTaskYAML]:
        p = Path(tasks_dir)
        if not p.exists():
            return []
        
        benchmarks = []
        for file in sorted(p.glob("*.yaml")) + sorted(p.glob("*.yml")):
            try:
                b = BenchmarkLoader.load_from_yaml(str(file))
                benchmarks.append(b)
            except Exception as e:
                print(f"[BenchmarkLoader] Warning: failed to parse {file}: {e}")
        return benchmarks

    @staticmethod
    def sync_benchmarks_to_db(db: Session, tasks_dir: str = "./benchmarks/tasks") -> List[str]:
        benchmarks = BenchmarkLoader.load_all_benchmarks(tasks_dir)
        repo = BenchmarkRepository(db)
        synced_ids = []

        for b in benchmarks:
            bench_data = {
                "id": b.id,
                "name": b.name,
                "description": b.description or "",
                "category": b.category,
                "difficulty": b.difficulty,
                "repo_type": b.repository.type,
                "repo_path": b.repository.path,
                "repo_commit": b.repository.commit
            }
            task_data = {
                "id": f"{b.id}-task",
                "prompt": b.task.prompt,
                "constraints": b.task.constraints or "",
                "evaluation_command": b.evaluation.command,
                "evaluation_timeout": b.evaluation.timeout,
                "scoring_weights": b.scoring.model_dump(),
                "env_vars": b.env or {}
            }
            repo.create_or_update(bench_data, task_data)
            synced_ids.append(b.id)

        return synced_ids
