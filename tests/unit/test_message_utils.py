from langchain.messages import AIMessage, HumanMessage, ToolMessage

from devops_agent.message_utils import extract_tool_calls


def test_extract_tool_calls_pairs_args_with_results():
    # Arrange: Build a fake message sequence like the agent will produce
    ai = AIMessage(
        content="",
        tool_calls=[{"id": "call_1", "name": "list_services", "args": {}}],
    )
    tool = ToolMessage(
        name="list_services",
        content="[]",
        tool_call_id="call_1",
    )
    msgs = [HumanMessage(content="list all"), ai, tool]

    # Act
    result = extract_tool_calls(msgs)

    # Assert
    assert len(result) == 1
    assert result[0]["name"] == "list_services"
    assert result[0]["args"] == {}
    assert result[0]["result"] == "[]"


def test_extract_tool_calls_returns_empty_when_no_tools():
    """A conversation with no tool calls should produce no entries."""
    msgs = [HumanMessage(content="hi")]
    assert extract_tool_calls(msgs) == []  # type: ignore


def test_extract_tool_calls_defaults_empty_args_when_id_missing():
    """A ToolMessage whose tool_call_id has no matching AIMessage falls back to empty args."""
    tool = ToolMessage(name="list_services", content="[]", tool_call_id="unknown_id")
    result = extract_tool_calls([tool])
    assert len(result) == 1
    assert result[0]["args"] == {}
