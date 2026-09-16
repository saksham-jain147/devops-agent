from typing import Protocol

from pydantic import BaseModel


class ServiceState(BaseModel):
    name: str
    status: str  # UP | DOWN | DEGRADED
    replicas: int
    version: str
    error_rate: float = 0.0


class InfraProvider(Protocol):
    def list_services(self) -> list[ServiceState]: ...
    def get_service(self, name: str) -> ServiceState | None: ...
    def get_logs(self, name: str, lines: int = 100) -> list[str]: ...
