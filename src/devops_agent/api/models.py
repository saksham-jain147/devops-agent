from pydantic import BaseModel

from devops_agent.agent.output import AgentAnswer


class QueryRequest(BaseModel):
    query: str
    dry_run: bool = True


QueryResponse = AgentAnswer
