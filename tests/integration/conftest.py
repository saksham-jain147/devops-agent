from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage  # noqa: F401


def make_fake_llm(scripted_responses: list):
    """Return a mock LLM that yields pre-scripted responses on each invoke call.

    scripted_responses: list of AIMessage objects, one per LLM turn.
    """
    fake = MagicMock()
    fake.bind_tools = MagicMock(return_value=fake)  # bind_tools() returns self
    fake.invoke = MagicMock(side_effect=scripted_responses)
    return fake


@pytest.fixture
def patch_llm(monkeypatch):
    """Fixture factory: pass in scripted responses, patches build_llm to return them."""

    def _patch(responses):
        fake = make_fake_llm(responses)
        monkeypatch.setattr("devops_agent.agent.graph.build_llm", lambda *a, **kw: fake)
        # Clear the graph cache so next request builds a fresh graph with the patched LLM
        from devops_agent.api.server import _get_graph

        _get_graph.cache_clear()
        return fake

    return _patch
