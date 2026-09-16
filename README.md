# DevOps Agent

**AI-powered SRE assistant for SaaS operations.** Natural-language queries against 
your infrastructure, backed by LangGraph + Claude/Gemini/Groq + Langfuse observability.

## Phase 1 — What works today

- [x] Multi-tool agent (LangGraph + tools) that answers questions about service state
- [x] Provider-agnostic LLM factory (Gemini / Groq / Anthropic swappable via env var)
- [x] Mock infrastructure with 4 services (auth, billing, notification, search)
- [x] 3 read tools: `list_services`, `get_service_status`, `get_service_logs`
- [x] FastAPI `/query` endpoint returning structured `AgentAnswer` (answer + tool traces)
- [x] Typer CLI (`devops-agent ask "..."`)
- [x] Unit tests for message correlation, mock provider, and tools
- [x] Integration tests for the API with scripted LLM responses

## Quickstart

```bash
# 1. Install
uv sync

# 2. Configure (copy .env.example → .env, add your API keys)
cp .env.example .env

# 3. Ask a question via CLI
uv run devops-agent ask "Why is billing-svc down?"

# Or start the API server
uv run uvicorn devops_agent.api.server:app --reload --port 8000
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "List all services"}'
