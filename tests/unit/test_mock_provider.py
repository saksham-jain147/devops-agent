import pytest

from devops_agent.infrastructure.base import ServiceState
from devops_agent.infrastructure.mock import MockProvider


def test_list_services_returns_all_four():
    # Arrange
    provider = MockProvider(flaky_rate=0.0)

    # Act
    services = provider.list_services()

    # Assert
    assert len(services) == 4


def test_list_services_returns_service_state_objects():
    provider = MockProvider(flaky_rate=0.0)
    services = provider.list_services()
    assert all(isinstance(s, ServiceState) for s in services)


def test_get_service_returns_correct_service_when_found():
    provider = MockProvider(flaky_rate=0.0)
    result = provider.get_service("billing-svc")
    assert result is not None
    assert result.name == "billing-svc"
    assert result.status == "down"


def test_get_service_returns_none_when_not_found():
    provider = MockProvider(flaky_rate=0.0)
    result = provider.get_service("nonexistent-svc")
    assert result is None


def test_get_services_returns_none_when_service_not_exists():
    provider = MockProvider(flaky_rate=0.0)
    result = provider.get_service("nonexistent-svc")
    assert result is None


@pytest.mark.parametrize(
    "service_name,expected_min_lines",
    [
        ("billing-svc", 3),
        ("notification-svc", 2),
    ],
)
def test_get_logs_returns_expected_line_count(service_name, expected_min_lines):
    provider = MockProvider(flaky_rate=0.0)
    logs = provider.get_logs(service_name)
    assert len(logs) >= expected_min_lines
