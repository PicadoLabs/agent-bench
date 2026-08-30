import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Enum as SqlEnum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BenchmarkModel(Base):
    __tablename__ = "benchmarks"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="Bug Fixing")  # Bug Fixing, Feature, Refactoring, Testing, Debugging
    difficulty = Column(String(20), nullable=False, default="Medium")  # Easy, Medium, Hard
    repo_type = Column(String(50), default="local")
    repo_path = Column(String(500), nullable=False)
    repo_commit = Column(String(100), default="HEAD")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    tasks = relationship("TaskModel", back_populates="benchmark", cascade="all, delete-orphan")
    runs = relationship("RunModel", back_populates="benchmark", cascade="all, delete-orphan")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String(100), primary_key=True)
    benchmark_id = Column(String(100), ForeignKey("benchmarks.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    constraints = Column(Text, nullable=True)
    evaluation_command = Column(String(500), nullable=False, default="pytest")
    evaluation_timeout = Column(Integer, default=120)
    scoring_weights = Column(JSON, default=lambda: {
        "correctness": 50,
        "test_pass_rate": 25,
        "code_quality": 10,
        "efficiency": 10,
        "reliability": 5
    })
    env_vars = Column(JSON, default=dict)
    metadata_json = Column(JSON, default=dict)

    benchmark = relationship("BenchmarkModel", back_populates="tasks")


class RunModel(Base):
    __tablename__ = "runs"

    id = Column(String(50), primary_key=True)  # e.g. RUN-0001
    benchmark_id = Column(String(100), ForeignKey("benchmarks.id"), nullable=False)
    benchmark_name = Column(String(200), nullable=True)
    task_id = Column(String(100), nullable=True)
    agent_name = Column(String(100), nullable=False, default="IterativeCodingAgent")
    model_name = Column(String(100), nullable=False, default="qwen2.5-coder")
    provider_name = Column(String(50), nullable=False, default="ollama")
    
    # States: QUEUED, PREPARING, RUNNING, TESTING, EVALUATING, SUCCEEDED, PARTIAL, FAILED, TIMEOUT, CRASHED, CANCELLED
    status = Column(String(30), nullable=False, default="QUEUED")
    
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    
    # Scores & Evaluation
    total_score = Column(Float, default=0.0)
    test_pass_rate = Column(Float, default=0.0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    
    # Execution metrics
    tool_calls_count = Column(Integer, default=0)
    commands_count = Column(Integer, default=0)
    retries_count = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    # Git & Output state
    git_diff = Column(Text, default="")
    logs = Column(Text, default="")
    repository_commit = Column(String(100), default="HEAD")
    agent_version = Column(String(50), default="1.0.0")
    config_snapshot = Column(JSON, default=dict)
    
    # Relationships
    benchmark = relationship("BenchmarkModel", back_populates="runs")
    tool_calls = relationship("ToolCallModel", back_populates="run", cascade="all, delete-orphan", order_by="ToolCallModel.step_number")
    execution_events = relationship("ExecutionEventModel", back_populates="run", cascade="all, delete-orphan", order_by="ExecutionEventModel.timestamp")
    test_results = relationship("TestResultModel", back_populates="run", cascade="all, delete-orphan")
    failure_analysis = relationship("FailureAnalysisModel", back_populates="run", uselist=False, cascade="all, delete-orphan")
    score_breakdown = relationship("ScoreModel", back_populates="run", uselist=False, cascade="all, delete-orphan")


class ToolCallModel(Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("runs.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    duration_seconds = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("RunModel", back_populates="tool_calls")


class ExecutionEventModel(Base):
    __tablename__ = "execution_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("runs.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # benchmark_started, tool_call, test_finished, etc.
    step_number = Column(Integer, default=0)
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("RunModel", back_populates="execution_events")


class TestResultModel(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("runs.id"), nullable=False)
    phase = Column(String(50), default="evaluation")  # initial, retry, final_evaluation
    command = Column(String(500), nullable=False)
    exit_code = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    test_details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("RunModel", back_populates="test_results")


class ScoreModel(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("runs.id"), nullable=False)
    correctness = Column(Float, default=0.0)
    test_pass_rate = Column(Float, default=0.0)
    code_quality = Column(Float, default=0.0)
    efficiency = Column(Float, default=0.0)
    reliability = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    breakdown = Column(JSON, default=dict)
    ai_judge_evaluation = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("RunModel", back_populates="score_breakdown")


class FailureAnalysisModel(Base):
    __tablename__ = "failure_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("runs.id"), nullable=False)
    # Categories: wrong_solution, incomplete_solution, test_failure, syntax_error, timeout, command_failure, tool_misuse, context_overflow, dependency_issue, permission_error, unknown
    primary_failure = Column(String(50), nullable=False, default="unknown")
    root_cause = Column(Text, nullable=True)
    failed_tests_count = Column(Integer, default=0)
    attempts_count = Column(Integer, default=1)
    resolution_hints = Column(Text, nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("RunModel", back_populates="failure_analysis")


class AgentRegistryModel(Base):
    __tablename__ = "agents"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    agent_type = Column(String(100), default="IterativeCodingAgent")
    description = Column(Text, nullable=True)
    version = Column(String(50), default="1.0.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ModelRegistryModel(Base):
    __tablename__ = "models"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    provider = Column(String(50), nullable=False)  # ollama, openai, anthropic, gemini, custom
    is_local = Column(Boolean, default=True)
    context_window = Column(Integer, default=32768)
    pricing_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
