from devops_agent.infrastructure.base import ServiceState

_SERVICES = {
    "auth-svc": ServiceState(
        name="auth-svc", status="up", replicas=3, version="v1.2.0", error_rate=0.001
    ),
    "billing-svc": ServiceState(
        name="billing-svc", status="down", replicas=0, version="v0.9.1", error_rate=1.0
    ),
    "notification-svc": ServiceState(
        name="notification-svc", status="degraded", replicas=2, version="v1.1.0", error_rate=0.12
    ),
    "search-svc": ServiceState(
        name="search-svc", status="up", replicas=4, version="v2.0.1", error_rate=0.003
    ),
}

_LOGS = {
    "billing-svc": [
        "2026-06-01T10:00:01Z ERROR Connection refused: postgres://billing-db:5432",
        "2026-06-01T10:00:02Z ERROR Connection refused: postgres://billing-db:5432",
        "2026-06-01T10:00:03Z FATAL Service shutting down after 3 failed db connects",
    ],
    "notification-svc": [
        "2026-06-01T10:00:00Z WARN SMTP timeout to smtp.provider.com",
        "2026-06-01T10:00:30Z WARN SMTP timeout to smtp.provider.com",
    ],
}


class MockProvider:
    def list_services(self) -> list[ServiceState]:
        return list(_SERVICES.values())

    def get_service(self, name: str) -> ServiceState | None:
        return _SERVICES.get(name)

    def get_logs(self, name: str, lines: int = 100) -> list[str]:
        return _LOGS.get(name, [])[:lines]
