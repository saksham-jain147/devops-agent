from unittest.mock import patch, MagicMock

import pytest

from devops_agent.agent.llm_factory import build_llm


@pytest.mark.parametrize("provider_name, mock_target", [
    ("gemini", "langchain_google_genai.ChatGoogleGenerativeAI"),
    ("groq", "langchain_groq.ChatGroq"),
    ("anthropic", "langchain_anthropic.ChatAnthropic"),
])
def test_build_llm_dispatches_to_correct_provider(provider_name, mock_target):
    with patch(mock_target) as mock_cls:
        mock_cls.return_value = MagicMock()
        build_llm(provider=provider_name)
    mock_cls.assert_called_once()


def test_build_llm_raises_on_unknown_provider():
    with pytest.raises(ValueError, match="unknown"):
        build_llm(provider="cohere")