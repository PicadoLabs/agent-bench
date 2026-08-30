import pytest
from app.providers.mock_provider import MockProvider
from app.providers.factory import get_provider
from app.providers.base import LLMMessage


@pytest.mark.asyncio
async def test_mock_provider_generation():
    provider = MockProvider(model_name="mock-coder")
    assert await provider.is_available() is True

    messages = [LLMMessage(role="user", content="Fix the issue")]
    resp = await provider.generate(messages=messages)
    assert resp is not None
    assert resp.provider_name == "mock"
    assert resp.total_tokens > 0


def test_provider_cost_calculation():
    provider = MockProvider(model_name="mock")
    pricing = {"input": 3.0, "output": 15.0}  # $3 / 1M in, $15 / 1M out
    cost = provider.calculate_cost(input_tokens=1000, output_tokens=500, pricing=pricing)
    # (1000 * 3 / 1e6) + (500 * 15 / 1e6) = 0.003 + 0.0075 = 0.0105
    assert cost == 0.0105
