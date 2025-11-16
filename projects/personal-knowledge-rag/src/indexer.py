"""CLI for indexing Obsidian vault."""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

from .knowledge_rag import KnowledgeRAG


console = Console()


@click.command()
@click.option(
    "--full",
    is_flag=True,
    help="Perform full reindex of entire vault"
)
@click.option(
    "--incremental",
    is_flag=True,
    default=True,
    help="Only index changed files (default)"
)
@click.option(
    "--vault-path",
    type=click.Path(exists=True),
    help="Override vault path from .env"
)
def index(full: bool, incremental: bool, vault_path: str):
    """Index Obsidian vault for semantic search.

    Examples:
        # Full reindex
        python -m src.indexer --full

        # Incremental update (default)
        python -m src.indexer --incremental
    """
    # TODO: Implement indexing CLI
    # 1. Load configuration from .env
    # 2. Initialize KnowledgeRAG
    # 3. Run indexing with progress bar
    # 4. Display statistics
    # 5. Show cost summary

    console.print("[yellow]⚠️  Indexer not yet implemented[/yellow]")


if __name__ == "__main__":
    index()
