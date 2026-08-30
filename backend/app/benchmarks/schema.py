from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RepositoryConfig(BaseModel):
    type: str = "local"
    path: str
    commit: str = "HEAD"


class TaskConfig(BaseModel):
    prompt: str
    constraints: Optional[str] = None


class EvaluationConfig(BaseModel):
    command: str = "pytest"
    timeout: int = 120


class ScoringWeights(BaseModel):
    correctness: float = 50.0
    test_pass_rate: float = 25.0
    code_quality: float = 10.0
    efficiency: float = 10.0
    reliability: float = 5.0


class BenchmarkTaskYAML(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str = "Bug Fixing"
    difficulty: str = "Medium"
    repository: RepositoryConfig
    task: TaskConfig
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    scoring: ScoringWeights = Field(default_factory=ScoringWeights)
    env: Optional[Dict[str, str]] = None
