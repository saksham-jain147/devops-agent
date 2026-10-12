from unittest.mock import patch

from typer.testing import CliRunner

from devops_agent.agent.output import AgentAnswer, ToolTrace
from devops_agent.cli import app

runner = CliRunner()


def test_ask_renders_answer_and_tool_calls():
    fake = AgentAnswer(
        answer="Fleet has 4 services.",
        confidence=0.9,
        tool_calls=[ToolTrace(name="list_services", args={}, result_summary="4 services")],
        prompt_version="v1",
    )
    with patch("devops_agent.cli.run_agent", return_value=fake):
        result = runner.invoke(app, ["ask", "list all services"])

    assert result.exit_code == 0
    assert "Fleet has 4 services" in result.stdout
    assert "list_services" in result.stdout


def test_version_command_runs():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
