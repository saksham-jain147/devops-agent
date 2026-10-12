import pytest
from langchain_core.messages import AIMessage  # noqa: F401


@pytest.fixture(autouse=True)
def _isolate_provider_from_env(monkeypatch):
    """Force inventory._provider to deterministic mode for every unit test.

    Prevents .env's MOCK_FLAKY_RATE from making test_tools tests non-deterministic.
    Tests that want to exercise flakiness should override explicitly.
    """
    from devops_agent.infrastructure.mock import MockProvider
    from devops_agent.tools import inventory

    monkeypatch.setattr(inventory, "_provider", MockProvider(flaky_rate=0.0))
