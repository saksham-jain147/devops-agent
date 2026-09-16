from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from devops_agent.agent.llm_factory import build_llm
from devops_agent.agent.state import AgentState
from devops_agent.config import settings
from devops_agent.tools.inventory import get_service_logs, get_service_status, list_services

TOOLS = [list_services, get_service_status, get_service_logs]


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
