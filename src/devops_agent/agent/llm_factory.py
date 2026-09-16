from langchain_core.language_models.chat_models import BaseChatModel

from devops_agent.config import settings


def build_llm(provider: str | None = None) -> BaseChatModel:
    """Build a chat model based on provider (defaults to settings.default_provider).

    This factory lets us swap providers via config without touching agent code.
    Providers are imported lazily so users only need the deps for what they use.
    """
    p = provider or settings.default_provider
    if p == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=settings.gemini_model, temperature=0)
    if p == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=settings.groq_model, temperature=0)
    if p == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model_name=settings.anthropic_model,
            temperature=0,
            max_tokens_to_sample=2048,
            timeout=None,
            stop=None,
        )
    raise ValueError(f"unknown provider: {p!r}. Expected: gemini | groq | anthropic")
