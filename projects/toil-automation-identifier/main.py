#!/usr/bin/env python3
"""
Toil Automation Identifier

Analyzes git commit history to identify repetitive tasks that should be automated.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from dotenv import load_dotenv

from git_analyzer import GitAnalyzer
from pattern_matcher import PatternMatcher
from automation_suggester import AutomationSuggester

# Load environment variables
load_dotenv()

console = Console()


def print_banner():
    """Print the application banner."""
    banner = """
[bold magenta]╭─────────────────────────────────────────────────────────────╮[/bold magenta]
[bold magenta]│[/bold magenta]  [bold cyan]🤖 Toil Automation Identifier[/bold cyan]                         [bold magenta]│[/bold magenta]
[bold magenta]│[/bold magenta]  [dim]Identify repetitive tasks worth automating[/dim]            [bold magenta]│[/bold magenta]
[bold magenta]╰─────────────────────────────────────────────────────────────╯[/bold magenta]
"""
    console.print(banner)


def analyze_repository(
    repo_path: str,
    commits: int,
    ai_provider: str = "none",
    min_pattern_count: int = 3,
) -> dict:
    """
    Analyze a repository for toil patterns.

    Args:
        repo_path: Path to git repository
        commits: Number of commits to analyze
        ai_provider: AI provider to use
        min_pattern_count: Minimum occurrences to report

    Returns:
        Analysis results dictionary
    """
    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Analyzing commits...", total=commits
        )

        # Step 1: Extract commits
        console.print(f"\n[bold]Repository:[/bold] {repo_path}")
        analyzer = GitAnalyzer(repo_path)
        repo_info = analyzer.get_repository_info()

        console.print(f"[bold]Branch:[/bold] {repo_info['active_branch']}")
        console.print(f"[bold]Analyzing:[/bold] {commits} commits\n")

        commit_messages = analyzer.get_commit_messages(max_count=commits)
        progress.update(task, advance=commits // 3)

        # Step 2: Pattern matching
        matcher = PatternMatcher(use_ai=(ai_provider != "none"))
        pattern_frequency = matcher.get_pattern_frequency(commit_messages)
        progress.update(task, advance=commits // 3)

        # Filter by minimum count
        pattern_frequency = [
            (name, count, cat)
            for name, count, cat in pattern_frequency
            if count >= min_pattern_count
        ]

        # Step 3: Generate suggestions
        suggester = AutomationSuggester()
        report = suggester.generate_report(pattern_frequency)
        progress.update(task, advance=commits // 3)

        return {
            "repo_info": repo_info,
            "total_commits_analyzed": len(commit_messages),
            "report": report,
            "pattern_frequency": pattern_frequency,
        }


def print_table_output(results: dict):
    """Print results in a rich table format."""
    report = results["report"]
    repo_info = results["repo_info"]

    # Summary panel
    summary = f"""[bold]Repository:[/bold] {repo_info['path']}
[bold]Branch:[/bold] {repo_info['active_branch']}
[bold]Commits Analyzed:[/bold] {results['total_commits_analyzed']}
[bold]Toil Commits Found:[/bold] {report['total_toil_commits']} ({report['total_toil_commits'] / results['total_commits_analyzed'] * 100:.1f}%)
[bold]Unique Patterns:[/bold] {report['unique_patterns']}
"""

    console.print(
        Panel(summary, title="📊 Analysis Summary", border_style="cyan")
    )
    console.print()

    if not report["recommendations"]:
        console.print(
            "[yellow]No significant toil patterns detected![/yellow]"
        )
        console.print(
            "[dim]Try analyzing more commits or lowering the minimum pattern count.[/dim]"
        )
        return

    # Main results table
    table = Table(
        title="🎯 Toil Patterns Ranked by Impact",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
    )

    table.add_column("Rank", style="dim", width=6)
    table.add_column("Pattern", style="cyan", width=25)
    table.add_column("Count", justify="right", width=10)
    table.add_column("Impact", justify="right", width=8)
    table.add_column("Difficulty", width=10)
    table.add_column("Automation Approach", width=30)

    for idx, rec in enumerate(report["recommendations"], 1):
        # Color code difficulty
        diff_color = {
            "easy": "green",
            "medium": "yellow",
            "hard": "red",
        }.get(rec["difficulty"], "white")

        table.add_row(
            str(idx),
            rec["pattern"],
            str(rec["frequency"]),
            f"{rec['impact_score']:.1f}",
            f"[{diff_color}]{rec['difficulty']}[/{diff_color}]",
            rec["approach"],
        )

    console.print(table)
    console.print()

    # Detailed recommendations for top 3
    console.print("[bold cyan]📝 Top 3 Recommendations:[/bold cyan]\n")

    for idx, rec in enumerate(report["recommendations"][:3], 1):
        console.print(f"[bold]{idx}. {rec['pattern']}[/bold]")
        console.print(f"   [dim]Frequency:[/dim] {rec['frequency']} commits")
        console.print(f"   [dim]Time Saved:[/dim] {rec['estimated_time_saved']}")
        console.print(f"   [dim]Tools:[/dim] {', '.join(rec['tools'])}")
        console.print(f"\n   [bold cyan]Setup Steps:[/bold cyan]")
        for step in rec["setup_steps"]:
            console.print(f"   • {step}")
        console.print(f"\n   [dim]Resources:[/dim]")
        for resource in rec["resources"]:
            console.print(f"   • {resource}")
        console.print()


def print_json_output(results: dict):
    """Print results in JSON format."""
    output = {
        "repository": results["repo_info"]["path"],
        "branch": results["repo_info"]["active_branch"],
        "commits_analyzed": results["total_commits_analyzed"],
        "toil_summary": {
            "total_toil_commits": results["report"]["total_toil_commits"],
            "unique_patterns": results["report"]["unique_patterns"],
        },
        "recommendations": results["report"]["recommendations"],
    }
    print(json.dumps(output, indent=2))


@click.command()
@click.option(
    "--repo",
    default=".",
    help="Path to git repository (default: current directory)",
)
@click.option(
    "--commits",
    default=lambda: int(os.getenv("COMMITS_TO_ANALYZE", "200")),
    help="Number of commits to analyze (default: 200)",
)
@click.option(
    "--ai",
    type=click.Choice(["none", "openai", "ollama"]),
    default=lambda: os.getenv("AI_PROVIDER", "none"),
    help="AI provider for enhanced analysis (default: none)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format (default: table)",
)
@click.option(
    "--min-count",
    default=lambda: int(os.getenv("MIN_PATTERN_COUNT", "3")),
    help="Minimum pattern occurrences to report (default: 3)",
)
def main(
    repo: str,
    commits: int,
    ai: str,
    output_format: str,
    min_count: int,
):
    """
    Analyze git repository to identify toil patterns worth automating.

    Examples:

        # Basic analysis of current repository
        python main.py

        # Analyze specific repository
        python main.py --repo /path/to/repo --commits 500

        # Use AI for better pattern detection
        python main.py --ai openai --commits 300

        # Output as JSON
        python main.py --format json > report.json
    """
    try:
        if output_format == "table":
            print_banner()

        results = analyze_repository(
            repo_path=repo,
            commits=commits,
            ai_provider=ai,
            min_pattern_count=min_count,
        )

        if output_format == "json":
            print_json_output(results)
        else:
            print_table_output(results)

            # Final tip
            console.print(
                Panel(
                    "[bold cyan]💡 Pro Tip:[/bold cyan] Start with the highest impact, easiest difficulty automation first!",
                    border_style="green",
                )
            )

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        console.print(
            f"[bold red]Unexpected error:[/bold red] {e}", file=sys.stderr
        )
        if os.getenv("DEBUG"):
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
