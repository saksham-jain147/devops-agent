from typing import Any

from langchain.messages import AIMessage, ToolMessage
from langchain_core.messages import BaseMessage


def extract_tool_calls(msgs: list[BaseMessage]) -> list[dict[str, Any]]:
    """Extract tool-call metadata (name, args, result) from a LangGraph message list.

    LangGraph splits a tool call into two messages: an AIMessage that decides
    which tool to call (carries args) and a ToolMessage with the result
    (carries content). This helper correlates them by tool_call_id.
    """
    # First pass: build id -> args lookup from AIMessages
    args_by_id: dict[str, Any] = {}
    for m in msgs:
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                tc_id = tc.get("id")
                if tc_id is None:
                    continue  # skip incomplete/streaming tool calls
                args_by_id[tc_id] = tc.get("args", {})

    # Second pass: pair each ToolMessage with its originating args
    return [
        {
            "name": m.name,
            "args": args_by_id.get(m.tool_call_id, {}),
            "result": m.content,
        }
        for m in msgs
        if isinstance(m, ToolMessage)
    ]
