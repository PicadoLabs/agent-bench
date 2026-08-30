from typing import Optional, Dict, Any
from app.agents.base import BaseAgent
from app.agents.iterative_coder import IterativeCodingAgent
from app.agents.baseline import BaselineAgent
from app.agents.fast_patch import FastPatchAgent
from app.providers.base import BaseModelProvider


def get_agent(
    agent_name: str,
    provider: BaseModelProvider,
    max_steps: int = 20,
    max_retries: int = 3,
    config: Optional[Dict[str, Any]] = None
) -> BaseAgent:
    name_clean = agent_name.lower().replace("-", "").replace("_", "").strip()

    if "baseline" in name_clean:
        return BaselineAgent(
            name=agent_name,
            provider=provider,
            max_steps=1,
            max_retries=0
        )
    elif "fast" in name_clean or "patch" in name_clean:
        return FastPatchAgent(
            name=agent_name,
            provider=provider,
            max_steps=2,
            max_retries=1
        )
    else:
        # Default IterativeCodingAgent
        return IterativeCodingAgent(
            name=agent_name,
            provider=provider,
            max_steps=max_steps,
            max_retries=max_retries
        )
