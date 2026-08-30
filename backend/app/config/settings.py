import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Global configuration settings for AgentBench."""
    
    # Core Model Settings
    model_provider: str = Field(default="ollama", env="MODEL_PROVIDER")
    model_name: str = Field(default="qwen2.5-coder", env="MODEL_NAME")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    
    # External API Keys (Optional)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    custom_api_base: Optional[str] = Field(default=None, env="CUSTOM_API_BASE")
    custom_api_key: Optional[str] = Field(default=None, env="CUSTOM_API_KEY")
    
    # Persistence
    database_url: str = Field(default="sqlite:///./agentbench.db", env="DATABASE_URL")
    
    # Sandboxing & Execution
    sandbox_runtime: str = Field(default="local", env="SANDBOX_RUNTIME")  # 'docker' or 'local'
    docker_image: str = Field(default="python:3.11-slim", env="DOCKER_IMAGE")
    default_timeout_seconds: int = Field(default=120, env="DEFAULT_TIMEOUT_SECONDS")
    max_agent_steps: int = Field(default=20, env="MAX_AGENT_STEPS")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # Server & API
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Benchmarks & Repositories Path
    benchmarks_dir: str = Field(default="./benchmarks", env="BENCHMARKS_DIR")
    workspaces_dir: str = Field(default="./sandbox_workspaces", env="WORKSPACES_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Pricing metadata per 1M tokens (Configurable, not hardcoded into business logic)
PROVIDER_PRICING: Dict[str, Dict[str, float]] = {
    "ollama": {
        "input_cost_per_million": 0.0,
        "output_cost_per_million": 0.0,
    },
    "mock": {
        "input_cost_per_million": 0.0,
        "output_cost_per_million": 0.0,
    },
    "openai": {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "default": {"input": 2.50, "output": 10.00}
    },
    "anthropic": {
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "default": {"input": 3.00, "output": 15.00}
    },
    "gemini": {
        "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
        "default": {"input": 0.50, "output": 1.50}
    }
}


def get_settings() -> Settings:
    return Settings()
