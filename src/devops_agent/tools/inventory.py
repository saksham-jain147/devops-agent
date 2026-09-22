from langchain_core.tools import tool
from pydantic import BaseModel, Field

from devops_agent.infrastructure.mock import MockProvider

_provider = MockProvider()


class ServiceSummary(BaseModel):
    name: str
    status: str = Field(..., description="up | down | degraded")
    replicas: int
    error_rate: float


class ListServicesOutput(BaseModel):
    services: list[ServiceSummary]
    total: int


class ServiceStatusOutput(BaseModel):
    """Structured status result for a single service."""

    found: bool = Field(..., description="whether the service exists in the fleet")
    service: ServiceSummary | None = Field(None, description="present only when found=True")
    error: str | None = Field(None, description="human-readable reason when found=False")
    requested_name: str = Field(
        ..., description="the name the caller asked about — useful for error context"
    )


class ServiceLogsOutput(BaseModel):
    """Structured log result for a single service."""

    service_name: str
    lines: list[str] = Field(default_factory=list, description="log lines in chronological order")
    line_count: int = Field(..., description="number of lines actually returned")
    truncated: bool = Field(..., description="True if the caller's line limit was hit")
    note: str | None = Field(None, description="informational message when no logs available")


@tool
def list_services() -> ListServicesOutput:
    """List all services with their current status, replicas, and error rate.
    Use this when the user asks about overall fleet state."""
    svcs = _provider.list_services()
    summaries = [
        ServiceSummary(name=s.name, status=s.status, replicas=s.replicas, error_rate=s.error_rate)
        for s in svcs
    ]
    return ListServicesOutput(services=summaries, total=len(summaries))


@tool
def get_service_status(service_name: str) -> ServiceStatusOutput:
    """Get current status, replicas, version, and error_rate for ONE service.
    Use after list_services to drill into a specific service.

    Args:
        service_name: exact name like "billing-svc"
    """
    svc = _provider.get_service(service_name)
    if not svc:
        return ServiceStatusOutput(
            found=False,
            service=None,
            error=f"service '{service_name}' not found in the fleet",
            requested_name=service_name,
        )
    return ServiceStatusOutput(
        found=True,
        service=ServiceSummary(
            name=svc.name,
            status=svc.status,
            replicas=svc.replicas,
            error_rate=svc.error_rate,
        ),
        error=None,
        requested_name=service_name,
    )


@tool
def get_service_logs(service_name: str, lines: int = 100) -> ServiceLogsOutput:
    """Return the most recent N lines of logs for a service.
    Use when diagnosing why a service is down or degraded.

    Args:
        service_name: exact name like "billing-svc"
        lines: max log lines to return (default 20)
    """
    logs = _provider.get_logs(service_name, lines)
    if not logs:
        return ServiceLogsOutput(
            service_name=service_name,
            lines=[],
            line_count=0,
            truncated=False,
            note=(
                f"no logs available for '{service_name}' — "
                "service may be new, quiet, or nonexistent"
            ),
        )
    return ServiceLogsOutput(
        service_name=service_name,
        lines=logs,
        line_count=len(logs),
        truncated=(len(logs) == lines),
        note=None,
    )
