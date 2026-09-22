import pytest  # noqa: F401

from devops_agent.tools.inventory import (
    ServiceSummary,
    get_service_logs,
    get_service_status,
    list_services,
)


def test_list_services_returns_four_services():
    result = list_services.invoke({})
    assert result.total == 4


def test_list_services_returns_dicts_with_expected_keys():
    result = list_services.invoke({})
    assert all(isinstance(s, ServiceSummary) for s in result.services)


def test_get_service_status_returns_correct_service_when_found():
    result = get_service_status.invoke({"service_name": "billing-svc"})
    assert result.service.name == "billing-svc"
    assert result.service.status == "down"


def test_get_service_status_returns_error_when_not_found():
    result = get_service_status.invoke({"service_name": "nonexistent-svc"})
    assert "not found" in result.error
    assert "nonexistent-svc" in result.error


def test_get_service_logs_returns_logs_for_service_with_logs():
    result = get_service_logs.invoke({"service_name": "billing-svc", "lines": 20})
    assert result.line_count > 0
    assert any("Connection refused" in item for item in result.lines)


def test_get_service_logs_returns_no_logs_message_for_service_without_logs():
    result = get_service_logs.invoke({"service_name": "auth-svc"})
    assert result.line_count == 0
    assert "no logs available" in result.note


def test_get_service_logs_respects_lines_limit():
    result = get_service_logs.invoke({"service_name": "billing-svc", "lines": 1})
    assert result.line_count == 1
