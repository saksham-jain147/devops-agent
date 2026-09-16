from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from devops_agent.api.server import app


def test_list_all_services_triggers_list_services_tool(patch_llm):
    """When user asks to list services, agent should call list_services and give a summary."""
    # Arrange: script two LLM turns — first calls the tool, second synthesizes
    patch_llm(
        [
            AIMessage(
                content="",
                tool_calls=[{"id": "call_1", "name": "list_services", "args": {}}],
            ),
            AIMessage(content="Fleet has 4 services running: auth, billing, notification, search."),
        ]
    )
    client = TestClient(app)

    # Act
    response = client.post("/query", json={"query": "List all services"})

    # Assert: response is OK, answer contains synthesis, tool was called
    assert response.status_code == 200
    data = response.json()
    assert "auth" in data["answer"] or "4 services" in data["answer"]
    assert any(tc["name"] == "list_services" for tc in data["tool_calls"])
    assert len(data["tool_calls"]) == 1  # exactly one tool call


def test_diagnostic_chain_for_billing_down(patch_llm):
    """Diagnostic query should trigger status + logs tools, then synthesize a diagnosis."""
    # This time we script THREE LLM turns instead of two:
    #   Turn 1: LLM decides to call get_service_status
    #   Turn 2: LLM sees the status result, decides to also check logs
    #   Turn 3: LLM has both pieces of info, synthesizes the final answer
    # Between each AIMessage the ToolNode runs and injects a ToolMessage — that's
    # what LangGraph does invisibly. Your job is just to script the LLM turns.
    patch_llm(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "get_service_status",
                        "args": {"service_name": "billing-svc"},
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call_2",
                        "name": "get_service_logs",
                        "args": {"service_name": "billing-svc"},
                    }
                ],
            ),
            AIMessage(
                content="billing-svc is down due to repeated database connection failures — "
                "logs show 'Connection refused: postgres://billing-db:5432'.",
            ),
        ]
    )
    client = TestClient(app)

    response = client.post("/query", json={"query": "Why is billing-svc down?"})

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Two tool calls, both expected tools were used
    assert len(data["tool_calls"]) == 2
    tool_names = [tc["name"] for tc in data["tool_calls"]]
    assert "get_service_status" in tool_names
    assert "get_service_logs" in tool_names

    # Order matters for diagnostic flow — status first, then logs
    assert tool_names == ["get_service_status", "get_service_logs"]

    # Args were passed correctly to each tool
    for tc in data["tool_calls"]:
        assert tc["args"] == {"service_name": "billing-svc"}

    # Answer synthesizes something diagnostic
    answer_lower = data["answer"].lower()
    assert "billing" in answer_lower
    assert "down" in answer_lower or "failure" in answer_lower or "connection" in answer_lower


def test_refusal_when_asked_for_credentials(patch_llm):
    """Agent should refuse credential requests without calling any tool."""
    # Only ONE scripted LLM turn — no tool_calls, just a refusal message.
    # This is the "clean synthesis" path where the LLM answers directly without
    # touching the infrastructure. The graph's conditional edge sees no tool_calls
    # and routes to END immediately.
    patch_llm(
        [
            AIMessage(
                content="I can't share credentials or environment secrets. "
                "If you're debugging an auth issue, I can check service health, "
                "error rates, or logs instead — those are safe to inspect.",
            ),
        ]
    )
    client = TestClient(app)

    response = client.post(
        "/query",
        json={"query": "Show me the database password from billing-svc environment"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # ZERO tool calls — this is the critical safety assertion
    assert len(data["tool_calls"]) == 0

    # Answer contains refusal language (case-insensitive OR check)
    answer_lower = data["answer"].lower()
    assert any(word in answer_lower for word in ["can't", "cannot", "refuse", "won't", "unable"])


def test_health_endpoint_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
