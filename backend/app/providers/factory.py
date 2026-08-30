from typing import Optional, Dict, Any
from app.config.settings import get_settings
from app.providers.base import BaseModelProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider


def get_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> BaseModelProvider:
    """Factory to get configured ModelProvider instance."""
    settings = get_settings()
    p_name = (provider_name or settings.model_provider).lower().strip()
    m_name = model_name or settings.model_name
    cfg = config or {}

    if p_name == "ollama":
        base_url = cfg.get("base_url", settings.ollama_base_url)
        return OllamaProvider(model_name=m_name, base_url=base_url, config=cfg)
    
    elif p_name in ["openai", "custom"]:
        api_key = cfg.get("api_key", settings.openai_api_key or settings.custom_api_key)
        base_url = cfg.get("base_url", settings.custom_api_base or "https://api.openai.com/v1")
        return OpenAIProvider(model_name=m_name, api_key=api_key, base_url=base_url, config=cfg)

    elif p_name == "anthropic":
        api_key = cfg.get("api_key", settings.anthropic_api_key)
        return AnthropicProvider(model_name=m_name, api_key=api_key, config=cfg)

    elif p_name == "gemini":
        api_key = cfg.get("api_key", settings.gemini_api_key)
        return GeminiProvider(model_name=m_name, api_key=api_key, config=cfg)

    elif p_name == "mock":
        return MockProvider(model_name=m_name, config=cfg)

    else:
        # Default fallback to Ollama
        return OllamaProvider(model_name=m_name, base_url=settings.ollama_base_url, config=cfg)
