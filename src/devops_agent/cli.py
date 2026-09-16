import typer
from langchain.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel

from devops_agent.agent.graph import build_graph

app = typer.Typer()
console = Console()


@app.command()
def ask(query: str):
    """Ask the DevOps agent a question."""
    graph = build_graph()
    out = graph.invoke({"messages": [HumanMessage(content=query)]})
    final = out["messages"][-1].content
    console.print(Panel(str(final), title="Agent answer", border_style="cyan"))


@app.command()
def version() -> None:
    """Show devops-agent version."""
    from importlib.metadata import version as _v

    typer.echo(_v("devops-agent"))


if __name__ == "__main__":
    app()
