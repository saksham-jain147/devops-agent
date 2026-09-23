from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    # LLM provider selection
    default_provider: str = "gemini"  # gemini | groq | anthropic

    # Per-provider API keys
    google_api_key: str = ""
    groq_api_key: str = ""
    anthropic_api_key: str = ""

    # Per-provider model names
    gemini_model: str = "gemini-2.0-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    anthropic_model: str = "claude-sonnet-5"

    # Eval judge
    judge_provider: str = "groq"
    judge_model: str = "llama-3.3-70b-versatile"

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # App
    log_level: str = "INFO"
    infra_provider: str = "mock"
    prompt_version: str = "v1"
    audit_log_path: str = "audit.log"

    # Agent Flakiness
    mock_flaky_rate: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
