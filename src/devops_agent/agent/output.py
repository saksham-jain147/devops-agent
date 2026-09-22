from pydantic import BaseModel, Field


class ToolTrace(BaseModel):
    name: str
    args: dict
    result_summary: str


class AgentAnswer(BaseModel):
    answer: str = Field(..., description="natural-language answer to the user")
    confidence: float = Field(..., ge=0.0, le=1.0, description="self-rated confidence 0-1")
    tool_calls: list[ToolTrace] = Field(default_factory=list)
    prompt_version: str
