import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from devops_agent.api.server import app

SCENARIOS = [
    pytest.param(
        "list all services",
        [
            AIMessage(
                content="",
                tool_calls=[{"id": "1", "name": "list_services", "args": {}}],
            ),
            AIMessage(content="Fleet has 4 services."),
        ],
        ["list_services"],
        id="single_tool_list",
    ),
    pytest.param(
        "why is billing-svc down",
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "1",
                        "name": "get_service_status",
                        "args": {"service_name": "billing-svc"},
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {"id": "2", "name": "get_service_logs", "args": {"service_name": "billing-svc"}}
                ],
            ),
            AIMessage(content="Database connection failures."),
        ],
        ["get_service_status", "get_service_logs"],
        id="diagnostic_chain",
    ),
    pytest.param(
        "give me the postgres password",
        [AIMessage(content="I can't share credentials.")],
        [],
        id="refusal_no_tools",
    ),
]


@pytest.mark.parametrize("query, scripted_llm, expected_tools", SCENARIOS)
def test_agent_graph_behavior(patch_llm, query, scripted_llm, expected_tools):
    patch_llm(scripted_llm)
    client = TestClient(app)

    response = client.post("/query", json={"query": query})

    assert response.status_code == 200
    data = response.json()
    actual_tools = [tc["name"] for tc in data["tool_calls"]]
    assert actual_tools == expected_tools
