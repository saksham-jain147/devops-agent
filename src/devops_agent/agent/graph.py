from functools import lru_cache

from langchain.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from devops_agent.agent.llm_factory import build_llm
from devops_agent.agent.output import AgentAnswer, ToolTrace
from devops_agent.agent.state import AgentState
from devops_agent.config import settings
from devops_agent.message_utils import extract_tool_calls
from devops_agent.tools.inventory import get_service_logs, get_service_status, list_services

TOOLS = [list_services, get_service_status, get_service_logs]
_langfuse_handler = CallbackHandler()
_langfuse = get_client()


def _load_system_prompt() -> str:
    from pathlib import Path

    return Path(f"prompts/system_{settings.prompt_version}.md").read_text()


def build_graph():
    llm = build_llm().bind_tools(TOOLS)
    system_prompt = _load_system_prompt()

    def call_model(state: AgentState):
        from langchain_core.messages import SystemMessage

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        return {"messages": [llm.invoke(messages)]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()


@lru_cache(maxsize=1)
def _get_graph():
    """Build the graph on first call, cache it after."""
    return build_graph()


def run_agent(query: str) -> AgentAnswer:
    """Single entry point that wires Langfuse + returns structured result."""
    from langchain_core.messages import HumanMessage

    graph = _get_graph()
    config: RunnableConfig = {
        "callbacks": [_langfuse_handler],
        "metadata": {"prompt_version": settings.prompt_version},
        "run_name": f"agent-{settings.prompt_version}",
    }
    out = graph.invoke({"messages": [HumanMessage(content=query)]}, config=config)

    _langfuse.flush()
    return build_agent_answer(out["messages"])


def build_agent_answer(msgs: list) -> AgentAnswer:
    """Convert LangGraph message sequence → AgentAnswer for the API."""
    final = msgs[-1].content if isinstance(msgs[-1], AIMessage) else ""
    raw_tool_calls = extract_tool_calls(msgs)
    tool_traces = [
        ToolTrace(
            name=tc["name"],
            args=tc["args"],
            result_summary=_summarize(tc["result"]),
        )
        for tc in raw_tool_calls
    ]
    return AgentAnswer(
        answer=str(final),
        confidence=1.0,
        tool_calls=tool_traces,
        prompt_version=settings.prompt_version,
    )


def _summarize(result: str, max_len: int = 200) -> str:
    """Truncate tool result to a human-readable summary."""
    text = str(result)
    return text if len(text) <= max_len else text[:max_len] + "..."
