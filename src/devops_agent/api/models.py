from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    dry_run: bool = True


class QueryResponse(BaseModel):
    answer: str
    tool_calls: list[dict]
