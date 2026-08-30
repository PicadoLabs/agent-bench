import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import get_settings
from app.storage.models import Base, AgentRegistryModel, ModelRegistryModel

settings = get_settings()

# SQLite engine with thread safety and WAL mode where possible
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes tables and seeds default built-in agents and models."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed default agents if empty
        if not db.query(AgentRegistryModel).first():
            default_agents = [
                AgentRegistryModel(
                    id="iterative-coder",
                    name="IterativeCodingAgent",
                    agent_type="Iterative ReAct Coding Agent",
                    description="Standard iterative agent that reads repository files, applies surgical patches, runs test suites, and iteratively fixes errors.",
                    version="1.0.0",
                    is_active=True
                ),
                AgentRegistryModel(
                    id="react-fast-coder",
                    name="FastPatchAgent",
                    agent_type="Single-pass Fast Patch Agent",
                    description="Rapid single-pass agent for simple bug fixes and quick modifications.",
                    version="1.0.0",
                    is_active=True
                ),
                AgentRegistryModel(
                    id="baseline-agent",
                    name="BaselineAgent",
                    agent_type="Zero-shot Baseline Agent",
                    description="Baseline agent for benchmark difficulty calibration and comparison without tool-assisted self-correction.",
                    version="1.0.0",
                    is_active=True
                )
            ]
            for a in default_agents:
                db.add(a)

        # Seed default models if empty
        if not db.query(ModelRegistryModel).first():
            default_models = [
                ModelRegistryModel(
                    id="qwen2.5-coder",
                    name="Qwen 2.5 Coder (Local)",
                    provider="ollama",
                    is_local=True,
                    context_window=32768,
                    pricing_metadata={"input": 0.0, "output": 0.0}
                ),
                ModelRegistryModel(
                    id="deepseek-coder-v2",
                    name="DeepSeek Coder V2 (Local)",
                    provider="ollama",
                    is_local=True,
                    context_window=64000,
                    pricing_metadata={"input": 0.0, "output": 0.0}
                ),
                ModelRegistryModel(
                    id="llama3.1",
                    name="Llama 3.1 8B (Local)",
                    provider="ollama",
                    is_local=True,
                    context_window=128000,
                    pricing_metadata={"input": 0.0, "output": 0.0}
                ),
                ModelRegistryModel(
                    id="gpt-4o",
                    name="OpenAI GPT-4o",
                    provider="openai",
                    is_local=False,
                    context_window=128000,
                    pricing_metadata={"input": 5.0, "output": 15.0}
                ),
                ModelRegistryModel(
                    id="gpt-4o-mini",
                    name="OpenAI GPT-4o Mini",
                    provider="openai",
                    is_local=False,
                    context_window=128000,
                    pricing_metadata={"input": 0.15, "output": 0.60}
                ),
                ModelRegistryModel(
                    id="claude-3-5-sonnet",
                    name="Claude 3.5 Sonnet",
                    provider="anthropic",
                    is_local=False,
                    context_window=200000,
                    pricing_metadata={"input": 3.0, "output": 15.0}
                ),
                ModelRegistryModel(
                    id="gemini-1.5-pro",
                    name="Gemini 1.5 Pro",
                    provider="gemini",
                    is_local=False,
                    context_window=1000000,
                    pricing_metadata={"input": 3.5, "output": 10.5}
                ),
                ModelRegistryModel(
                    id="gemini-1.5-flash",
                    name="Gemini 1.5 Flash",
                    provider="gemini",
                    is_local=False,
                    context_window=1000000,
                    pricing_metadata={"input": 0.35, "output": 1.05}
                )
            ]
            for m in default_models:
                db.add(m)

        db.commit()
    finally:
        db.close()
