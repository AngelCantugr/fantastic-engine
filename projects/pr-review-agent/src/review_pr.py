"""CLI for reviewing pull requests."""

import click
from rich.console import Console
from rich.progress import Progress

from .pr_review_agent import PRReviewAgent


console = Console()


@click.command()
@click.option(
    "--pr",
    type=int,
    required=True,
    help="PR number to review"
)
@click.option(
    "--categories",
    default="bugs,security,style,performance",
    help="Comma-separated review categories"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Don't post comments, just analyze"
)
@click.option(
    "--repo",
    help="Override repo from .env"
)
def review(pr: int, categories: str, dry_run: bool, repo: str):
    """Review a pull request with AI.

    Examples:
        # Review PR #123
        python -m src.review_pr --pr 123

        # Review with specific categories
        python -m src.review_pr --pr 123 --categories bugs,security

        # Dry run (don't post comments)
        python -m src.review_pr --pr 123 --dry-run
    """
    # TODO: Implement PR review CLI
    # 1. Load configuration from .env
    # 2. Initialize PRReviewAgent
    # 3. Run review with progress bar
    # 4. Display results with Rich formatting
    # 5. Show cost summary

    console.print(f"[cyan]🤖 Reviewing PR #{pr}[/cyan]")

    if dry_run:
        console.print("[yellow]🔍 Dry run mode - no comments will be posted[/yellow]")

    console.print("[yellow]⚠️  Review not yet implemented[/yellow]")


if __name__ == "__main__":
    review()
