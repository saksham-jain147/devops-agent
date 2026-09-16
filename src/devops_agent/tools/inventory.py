from langchain_core.tools import tool

from devops_agent.infrastructure.mock import MockProvider

_provider = MockProvider()


@tool
def list_services() -> list[dict]:
    """List all services with their current status, replicas, and error rate.
    Use this when the user asks about overall fleet state."""
    return [s.model_dump() for s in _provider.list_services()]


@tool
def get_service_status(service_name: str) -> dict:
    """Get current status, replicas, version, and error_rate for ONE service.
    Use after list_services to drill into a specific service.

    Args:
        service_name: exact name like "billing-svc"
    """
    svc = _provider.get_service(service_name)
    if not svc:
        return {"error": f"service '{service_name}' not found"}
    return svc.model_dump()


@tool
def get_service_logs(service_name: str, lines: int = 100) -> list[str]:
    """Return the most recent N lines of logs for a service.
    Use when diagnosing why a service is down or degraded.

    Args:
        service_name: exact name like "billing-svc"
        lines: max log lines to return (default 20)
    """
    logs = _provider.get_logs(service_name, lines)
    if not logs:
        return [f"no logs found for '{service_name}"]
    return logs
