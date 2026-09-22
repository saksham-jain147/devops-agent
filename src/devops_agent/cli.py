import typer
from rich.console import Console
from rich.panel import Panel

from devops_agent.agent.graph import run_agent

app = typer.Typer()
console = Console()


@app.command()
def ask(query: str):
    """Ask the DevOps agent a question."""
    out = run_agent(query)

    console.print(Panel(out.answer, title="Answer", border_style="cyan"))

    if out.tool_calls:
        console.print("\n[bold]Tool calls:[/bold]")
        for tc in out.tool_calls:
            console.print(f"  • [green]{tc.name}[/green]({tc.args}) -> {tc.result_summary}")

    console.print(f"\n[dim]confidence={out.confidence} · prompt={out.prompt_version}[/dim]")



@app.command()
def version() -> None:
    """Show devops-agent version."""
    from importlib.metadata import version as _v

    typer.echo(_v("devops-agent"))


if __name__ == "__main__":
    app()
