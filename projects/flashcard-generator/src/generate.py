"""CLI for generating flashcards."""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from .flashcard_generator import FlashcardGenerator


console = Console()


@click.command()
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="Generate from single file"
)
@click.option(
    "--vault",
    type=click.Path(exists=True),
    help="Generate from entire vault"
)
@click.option(
    "--folder",
    help="Specific folder in vault (requires --vault)"
)
@click.option(
    "--tags",
    help="Filter by tags (comma-separated)"
)
@click.option(
    "--output",
    default="./output/anki_cards.csv",
    help="Output CSV file path"
)
@click.option(
    "--min-quality",
    type=int,
    default=7,
    help="Minimum quality score (1-10)"
)
def generate(file: str, vault: str, folder: str, tags: str, output: str, min_quality: int):
    """Generate Anki flashcards from Obsidian notes.

    Examples:
        # Single file
        python -m src.generate --file note.md

        # Entire vault
        python -m src.generate --vault /path/to/vault

        # Specific folder with tags
        python -m src.generate --vault /path/to/vault --folder Learning --tags python,async
    """
    # TODO: Implement flashcard generation CLI
    # 1. Load configuration from .env
    # 2. Initialize FlashcardGenerator
    # 3. Generate cards based on mode (file/vault)
    # 4. Filter by quality
    # 5. Display summary with Rich
    # 6. Export to CSV
    # 7. Show cost summary

    console.print("[cyan]🎴 Flashcard Generator v0.1.0[/cyan]")

    if file:
        console.print(f"[green]📝 Processing file: {file}[/green]")
        console.print("[yellow]⚠️  File generation not yet implemented[/yellow]")
    elif vault:
        console.print(f"[green]📚 Processing vault: {vault}[/green]")
        if folder:
            console.print(f"[blue]📁 Folder: {folder}[/blue]")
        if tags:
            console.print(f"[blue]🏷️  Tags: {tags}[/blue]")
        console.print("[yellow]⚠️  Vault generation not yet implemented[/yellow]")
    else:
        console.print("[red]Error:[/red] Specify --file or --vault")


if __name__ == "__main__":
    generate()
