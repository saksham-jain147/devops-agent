from functools import lru_cache

from fastapi import FastAPI
from langchain.messages import AIMessage, HumanMessage

from devops_agent.agent.graph import build_graph
from devops_agent.api.models import QueryRequest, QueryResponse
from devops_agent.message_utils import extract_tool_calls

app = FastAPI(title="Devops Agent")


@lru_cache(maxsize=1)
def _get_graph():
    """Build the graph on first call, cache it after."""
    return build_graph()


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    out = _get_graph().invoke({"messages": [HumanMessage(content=req.query)]})
    msgs = out["messages"]
    final = msgs[-1].content if isinstance(msgs[-1], AIMessage) else ""
    tool_calls = extract_tool_calls(msgs)
    return QueryResponse(answer=str(final), tool_calls=tool_calls)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
