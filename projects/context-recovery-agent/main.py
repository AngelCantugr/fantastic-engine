#!/usr/bin/env python3
"""CLI entry point for Context Recovery Agent."""

import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from context_agent import ContextRecoveryAgent

app = typer.Typer(help="🧠 Context Recovery Agent - Resume work after interruptions")
console = Console()


@app.command()
def main(
    repo: Optional[Path] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Path to git repository (defaults to current directory)"
    ),
    vault: Optional[Path] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Path to Obsidian vault (defaults to configured path or auto-detect)"
    ),
    ticktick_url: str = typer.Option(
        "http://localhost:3000",
        "--ticktick-url",
        "-t",
        help="TickTick MCP server URL"
    ),
    provider: str = typer.Option(
        "openai",
        "--provider",
        "-p",
        help="AI provider: openai or ollama"
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="AI model name (e.g., gpt-4, llama3)"
    ),
    commits: int = typer.Option(
        3,
        "--commits",
        "-c",
        help="Number of recent git commits to analyze"
    ),
    days: int = typer.Option(
        1,
        "--days",
        "-d",
        help="Number of days of notes to include"
    ),
):
    """
    Analyze your recent work and help you resume where you left off.

    This tool analyzes:
    - Recent git commits
    - Recent Obsidian notes
    - Active TickTick tasks

    And generates an AI-powered summary of:
    - What you were working on
    - Next logical steps
    - Blockers and context
    """
    try:
        # Create and run agent
        agent = ContextRecoveryAgent(
            repo_path=repo,
            vault_path=vault,
            ticktick_url=ticktick_url,
            ai_provider=provider,
            ai_model=model
        )

        agent.run(commit_count=commits, note_days=days)

    except KeyboardInterrupt:
        console.print("\n\n👋 Interrupted by user")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n❌ [red]Error: {e}[/red]")
        if "--debug" in sys.argv:
            raise
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
