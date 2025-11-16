"""CLI for searching Obsidian vault."""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .knowledge_rag import KnowledgeRAG


console = Console()


@click.command()
@click.argument("query", required=False)
@click.option(
    "--tags",
    help="Filter by tags (comma-separated)"
)
@click.option(
    "--top-k",
    type=int,
    default=5,
    help="Number of results to return"
)
@click.option(
    "--interactive",
    is_flag=True,
    help="Interactive search mode"
)
def search(query: str, tags: str, top_k: int, interactive: bool):
    """Search Obsidian vault with natural language.

    Examples:
        # Direct query
        python -m src.search "How do I use async/await in Rust?"

        # With filters
        python -m src.search "machine learning" --tags "ai,ml" --top-k 10

        # Interactive mode
        python -m src.search --interactive
    """
    # TODO: Implement search CLI
    # 1. Load configuration from .env
    # 2. Initialize KnowledgeRAG
    # 3. If interactive, start REPL
    # 4. Otherwise, run query
    # 5. Format and display results with Rich
    # 6. Show cost/time statistics

    if interactive:
        console.print("[cyan]🔍 Interactive Search Mode[/cyan]")
        console.print("[yellow]⚠️  Not yet implemented[/yellow]")
    elif query:
        console.print(f"[cyan]🔍 Query:[/cyan] {query}")
        console.print("[yellow]⚠️  Search not yet implemented[/yellow]")
    else:
        console.print("[red]Error:[/red] Provide a query or use --interactive")


if __name__ == "__main__":
    search()
