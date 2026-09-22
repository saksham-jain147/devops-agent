from fastapi import FastAPI

from devops_agent.agent.graph import run_agent
from devops_agent.api.models import QueryRequest, QueryResponse

app = FastAPI(title="Devops Agent")


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    return run_agent(req.query)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
